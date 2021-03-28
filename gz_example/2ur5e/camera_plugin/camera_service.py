import cv2
import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import RobotRaconteurCompanion as RRC
import argparse
import sys
import platform
import threading, traceback
import numpy as np
from RobotRaconteurCompanion.Util.InfoFileLoader import InfoFileLoader
from RobotRaconteurCompanion.Util.DateTimeUtil import DateTimeUtil
from RobotRaconteurCompanion.Util.SensorDataUtil import SensorDataUtil
from RobotRaconteurCompanion.Util.AttributesUtil import AttributesUtil

class CameraImpl(object):
    
    def __init__(self, camera_sim_path, camera_info):
        
        self._seqno = 0

        self.server = RRN.ConnectService('rr+tcp://localhost:11346?service=GazeboServer')# Gazebo server
        print(self.server.sensor_names)
        self._capture = self.server.get_sensors(camera_sim_path)

        self._imaging_consts = RRN.GetConstants('com.robotraconteur.imaging')
        self._image_consts = RRN.GetConstants('com.robotraconteur.image')
        self._image_type = RRN.GetStructureType('com.robotraconteur.image.Image')
        self._image_info_type = RRN.GetStructureType('com.robotraconteur.image.ImageInfo')
        self._compressed_image_type = RRN.GetStructureType('com.robotraconteur.image.CompressedImage')
        self._date_time_utc_type = RRN.GetPodDType('com.robotraconteur.datetime.DateTimeUTC')
        self._isoch_info = RRN.GetStructureType('com.robotraconteur.device.isoch.IsochInfo')
        self._capture_lock = threading.Lock()
        self._streaming = False
        self._fps = 30
        self._camera_info = camera_info
        self._date_time_util = DateTimeUtil(RRN)
        self._sensor_data_util = SensorDataUtil(RRN)

    def RRServiceObjectInit(self, ctx, service_path):
        self._downsampler = RR.BroadcastDownsampler(ctx)
        self._downsampler.AddPipeBroadcaster(self.frame_stream)
        self._downsampler.AddPipeBroadcaster(self.frame_stream_compressed)
        self._downsampler.AddPipeBroadcaster(self.preview_stream)
        self._downsampler.AddWireBroadcaster(self.device_clock_now)
        self.frame_stream.MaxBacklog = 2
        self.frame_stream_compressed.MaxBacklog = 2
        self.preview_stream.MaxBacklog = 2
        
        # TODO: Broadcaster peek handler in Python
        # self.device_clock_now.PeekInValueCallback = lambda ep: self._date_time_util.FillDeviceTime(self._camera_info.device_info,self._seqno)

    @property
    def device_info(self):
        return self._camera_info.device_info

    @property
    def camera_info(self):
        return self._camera_info

    def _cv_mat_to_image(self, mat):

        is_mono = False
        if (len(mat.shape) == 2 or mat.shape[2] == 1):
            is_mono = True

        image_info = self._image_info_type()
        image_info.width =mat.shape[1]
        image_info.height = mat.shape[0]
        if is_mono:
            image_info.step = mat.shape[1]
            image_info.encoding = self._image_consts["ImageEncoding"]["mono8"]
        else:
            image_info.step = mat.shape[1]*3
            image_info.encoding = self._image_consts["ImageEncoding"]["rgb8"]
        image_info.data_header = self._sensor_data_util.FillSensorDataHeader(self._camera_info.device_info,self._seqno)
        

        image = self._image_type()
        image.image_info = image_info
        image.data=mat.reshape(mat.size, order='C')
        return image

    def _cv_mat_to_compressed_image(self, mat, quality = 100):

        is_mono = False
        if (len(mat.shape) == 2 or mat.shape[2] == 1):
            is_mono = True

        image_info = self._image_info_type()
        image_info.width =mat.shape[1]
        image_info.height = mat.shape[0]
        
        image_info.step = 0
        image_info.encoding = self._image_consts["ImageEncoding"]["compressed"]
        image_info.data_header = self._sensor_data_util.FillSensorDataHeader(self._camera_info.device_info,self._seqno)
        
        image = self._compressed_image_type()
        image.image_info = image_info
        res, encimg = cv2.imencode(".jpg",mat,[int(cv2.IMWRITE_JPEG_QUALITY), quality])
        assert res, "Could not compress frame!"
        image.data=encimg
        return image

    def ImageToMat(self, image):
        frame2=image.data.reshape([image.image_info.height, image.image_info.width, 3], order='C')
        return np.concatenate((np.atleast_3d(frame2[:,:,2]), np.atleast_3d(frame2[:,:,1]), np.atleast_3d(frame2[:,:,0])),axis=2)

    def capture_frame(self):
        with self._capture_lock:
            img = self._capture.capture_image()
        return img

    def capture_frame_compressed(self):
        with self._capture_lock:
            img = self._capture.capture_image()
            mat = self.ImageToMat(img)
        return self._cv_mat_to_compressed_image(mat)

    def trigger(self):
        raise RR.NotImplementedException("Not available on this device")

    def frame_threadfunc(self):
        while(self._streaming):
            with self._capture_lock:
                img = self._capture.capture_image()
                mat = self.ImageToMat(img)
                self._seqno+=1
            
            self.frame_stream.AsyncSendPacket(self._cv_mat_to_image(mat),lambda: None)
            self.frame_stream_compressed.AsyncSendPacket(self._cv_mat_to_compressed_image(mat),lambda: None)
            self.preview_stream.AsyncSendPacket(self._cv_mat_to_compressed_image(mat,70),lambda: None)
            device_now = self._date_time_util.FillDeviceTime(self._camera_info.device_info,self._seqno)
            self.device_clock_now.OutValue = device_now

    def start_streaming(self):
        if (self._streaming):
            raise RR.InvalidOperationException("Already streaming")
        self._streaming=True
        t=threading.Thread(target=self.frame_threadfunc)
        t.start()

    def stop_streaming(self):
        if (not self._streaming):
            raise RR.InvalidOperationException("Not streaming")
        self._streaming=False

    @property
    def isoch_downsample(self):
        return self._downsampler.GetClientDownsample(RR.ServerEndpoint.GetCurrentEndpoint())

    @isoch_downsample.setter
    def isoch_downsample(self, value):
        return self._downsampler.SetClientDownsample(RR.ServerEndpoint.GetCurrentEndpoint(),value)

    @property
    def isoch_info(self):
        ret = self._isoch_info()
        ret.update_rate = self._fps
        ret.max_downsample = 100
        ret.isoch_epoch = np.zeros((1,),dtype=self._date_time_utc_type)

    @property
    def capabilities(self):
        return 0x1 | 0x2 | 0x4

    

def main():
    parser = argparse.ArgumentParser(description="OpenCV based camera driver service for Robot Raconteur Emulator for Gazebo Simulation Worlds with Camera Sensors")
    parser.add_argument("--camera-info-file", type=argparse.FileType('r'),default=None,required=True,help="Camera info file (required)")
    parser.add_argument("--camera-sim-path", type=str, default="default::camera::link::camera", help="Specify the camera path in the simulation world (default 'default::rip::pendulum::camera')")
    parser.add_argument("--wait-signal",action='store_const',const=True,default=False, help="wait for SIGTERM orSIGINT (Linux only)")

    args, _ = parser.parse_known_args()

    rr_args = ["--robotraconteur-jumbo-message=true"] + sys.argv
    with RR.ServerNodeSetup("com.robotraconteur.imaging.camera",59823,argv=rr_args):
        try:
            #RRN.RegisterServiceTypesFromFiles(['com.robotraconteur.imaging'],True)
            RRC.RegisterStdRobDefServiceTypes(RRN)

            with args.camera_info_file:
                camera_info_text = args.camera_info_file.read()

            info_loader = InfoFileLoader(RRN)
            camera_info, camera_ident_fd = info_loader.LoadInfoFileFromString(camera_info_text, "com.robotraconteur.imaging.camerainfo.CameraInfo", "camera")

            attributes_util = AttributesUtil(RRN)
            camera_attributes = attributes_util.GetDefaultServiceAttributesFromDeviceInfo(camera_info.device_info)

            camera = CameraImpl(args.camera_sim_path,camera_info)
            for _ in range(10):
                camera.capture_frame()
        
        

            service_ctx = RRN.RegisterService("camera","com.robotraconteur.imaging.Camera",camera)
            service_ctx.SetServiceAttributes(camera_attributes)

            if args.wait_signal:  
                #Wait for shutdown signal if running in service mode          
                print("Press Ctrl-C to quit...")
                import signal
                signal.sigwait([signal.SIGTERM,signal.SIGINT])
            else:
                #Wait for the user to shutdown the service
                if (sys.version_info > (3, 0)):
                    input("Server started, press enter to quit...")
                else:
                    raw_input("Server started, press enter to quit...")
        except:
            traceback.print_exc()

if __name__ == "__main__":
    main()