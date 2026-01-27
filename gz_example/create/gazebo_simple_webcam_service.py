#Simple example Robot Raconteur webcam service

#Note: This example is intended to demonstrate Robot Raconteur
#and is designed to be simple rather than optimal.

import time
import RobotRaconteur as RR
#Convenience shorthand to the default node.
#RRN is equivalent to RR.RobotRaconteurNode.s
RRN=RR.RobotRaconteurNode.s
import threading
import numpy
import traceback
import platform
import sys
import argparse
import drekar_launch_process

#Class that implements a single webcam
class Webcam_impl(object):
    #Init the camera being passed the camera number and the camera name
    def __init__(self,cameraid,cameraname,gazebo_server):
        self._lock=threading.RLock()
        self._framestream=None
        self._framestream_endpoints=dict()
        self._framestream_endpoints_lock=threading.RLock()
        self._streaming=False
        self._cameraname=cameraname
        self._gazebo_server = gazebo_server

        self._webcamimage_type = RRN.GetStructureType("experimental.simplewebcam3.WebcamImage")
        self._webcamimage_size_type = RRN.GetStructureType("experimental.simplewebcam3.WebcamImage_size")


        #Create buffers for memory members
        self._buffer=numpy.array([],dtype="u1")
        self._multidimbuffer=numpy.array([],dtype="u1")

        #Initialize the camera
        if cameraid == 0:
            camera_sim_path = "default::rr_create::base::left_camera"
        else:
            camera_sim_path = "default::rr_create::base::right_camera"

        # Encode argument in service path with URL % escape
        camera_sim_service_path="*.sensors[" + "".join([(s if s.isalpha() else '%{:02X}'.format(ord(s))) for s in camera_sim_path]) + "]"

        self._frame = None
        self._camera_pipe_sub = self._gazebo_server.SubscribePipe("image_stream",camera_sim_service_path)
        self._camera_pipe_sub.PipePacketReceived += self._new_packets

    def _new_packets(self,pipe_sub):
        with self._lock:
            try:
                while pipe_sub.Available > 0:
                        rr_image = pipe_sub.ReceivePacket()
                if rr_image is None:
                    return
                if rr_image.image_info.encoding == 0x1002:
                    self._frame = rr_image.data.reshape([rr_image.image_info.height,rr_image.image_info.width,3])
                if rr_image.image_info.encoding == 0x1000:
                    mat = rr_image.data.reshape([rr_image.image_info.height,rr_image.image_info.width,3])
                    self._frame = mat = mat[:, :, [2, 1, 0]]
            except:
                traceback.print_exc()

    #Return the camera name
    @property
    def name(self):
        return self._cameraname

    #Capture a frame and return a WebcamImage structure to the client
    def capture_frame(self):
        with self._lock:
            image = self._webcamimage_type()
            frame = self._frame
            if frame is None:
                raise Exception("Could not read from webcam")
            image.width=frame.shape[1]
            image.height=frame.shape[0]
            image.step=frame.shape[1]*3
            image.data=frame.reshape(frame.size, order='C')

            return image

    #Start the thread that captures images and sends them through connected
    #FrameStream pipes
    def start_streaming(self):
        if (self._streaming):
            raise Exception("Already streaming")
        self._streaming=True
        t=threading.Thread(target=self.frame_threadfunc)
        t.start()

    #Stop the streaming thread
    def stop_streaming(self):
        if (not self._streaming):
            raise Exception("Not streaming")
        self._streaming=False

    #Function that will send a frame at ideally 4 fps, although in reality it
    #will be lower because Python is quite slow.  This is for
    #demonstration only...
    def frame_threadfunc(self):
        #Loop as long as we are streaming
        while(self._streaming):
            #Capture a frame
            try:
                frame=self.capture_frame()
            except:
                #TODO: notify the client that streaming has failed
                self._streaming=False
                return
            #Send the new frame to the broadcaster.  Use AsyncSendPacket
            #and a blank handler.  We really don't care when the send finishes
            #since we are using the "backlog" flow control in the broadcaster.
            self._framestream.AsyncSendPacket(frame,lambda: None)

            #Put in a 100 ms delay
            time.sleep(.1)

    #Captures a frame and places the data in the memory buffers
    def capture_frame_to_buffer(self):
        with self._lock:
            #Capture and image and place it into the buffer
            image=self.capture_frame()
    
            self._buffer=image.data
            self._multidimbuffer=numpy.concatenate((image.data[2::3].reshape((image.height,image.width,1)),image.data[1::3].reshape((image.height,image.width,1)),image.data[0::3].reshape((image.height,image.width,1))),axis=2)
    
            #Create and populate the size structure and return it
            size=self._webcamimage_size_type()
            size.height=image.height
            size.width=image.width
            size.step=image.step
            return size

    #Return the memories.  It would be better to reuse the memory objects,
    #but for simplicity return new instances when called
    @property
    def buffer(self):
        return RR.ArrayMemory(self._buffer)

    @property
    def multidimbuffer(self):
        return RR.MultiDimArrayMemory(self._multidimbuffer)


    #Shutdown the Webcam
    def _shutdown(self):
        self._streaming=False
        


#A root class that provides access to multiple cameras
class WebcamHost_impl(object):
    def __init__(self,camera_names, gazebo_url):

        self._gazebo_server = RRN.SubscribeService(gazebo_url)

        cams=dict()        
        for i in camera_names:
            ind,name=i
            cam=Webcam_impl(ind,name,self._gazebo_server)
            cams[ind]=cam

        self._cams=cams


    #Returns a map (dict in Python) of the camera names
    @property
    def webcam_names(self):
        o=dict()
        for ind in self._cams.keys():
            name=self._cams[ind].Name
            o[ind]=name
        return o

    #objref function to return Webcam objects
    def get_webcams(self,ind):
        #The index for the object may come as a string, so convert to int
        #before using. This is only necessary in Python
        int_ind=int(ind)

        #Return the object and the Robot Raconteur type of the object
        return self._cams[int_ind], "experimental.simplewebcam3.Webcam"

    #Shutdown all the webcams
    def _shutdown(self):
        for cam in self._cams.values():
            cam._shutdown()



def main():

    #Accept the names of the webcams and the nodename from command line
            
    parser = argparse.ArgumentParser(description="Example Robot Raconteur webcam service")
    parser.add_argument("--camera-names",type=str,help="List of camera names separated with commas")
    parser.add_argument("--gazebo-url",type=str,
        default="rr+tcp://localhost:11346/?service=GazeboServer",
        help="The URL for the Gazebo plugin. Default 'rr+tcp://localhost:11346/?service=GazeboServer'")
    args, _ = parser.parse_known_args()

    #Initialize the webcam host root object
    camera_names=[(0,"Left"),(1,"Right")]
    if args.camera_names is not None:
        camera_names_split=list(filter(None,args.camera_names.split(',')))
        assert(len(camera_names_split) > 0)
        camera_names = [(i,camera_names_split[i]) for i in range(len(camera_names_split))]
        
        
    
    RRN.RegisterServiceType(_robdef)
    with RR.ServerNodeSetup("experimental.simplewebcam3_multi", 22355, argv=sys.argv):
        obj=WebcamHost_impl(camera_names, args.gazebo_url)

        RRN.RegisterService("multiwebcam","experimental.simplewebcam3.WebcamHost",obj)
    
        #c1=obj.get_Webcams(0)[0]
        #c1.CaptureFrameToBuffer()
    
        drekar_launch_process.wait_exit()
    
        #Shutdown
        obj._shutdown()    

_robdef = \
"""
#Service to provide sample interface to webcams

# This interface is for example only. Most cameras should use the standard com.robotraconteur.imaging.Camera interface
service experimental.simplewebcam3

# The current version of Robot Raconteur robdef standards is 0.10
stdver 0.10

struct WebcamImage
    field int32 width
    field int32 height
    field int32 step
    field uint8[] data
end

struct WebcamImage_size
    field int32 width
    field int32 height
    field int32 step
end

object Webcam
    property string name [readonly]
    function WebcamImage capture_frame()

    function void start_streaming()
    function void stop_streaming()
    pipe WebcamImage frame_stream [readonly]

    function WebcamImage_size capture_frame_to_buffer()
    memory uint8[] buffer [readonly]
    memory uint8[*] multidimbuffer [readonly]

end

object WebcamHost
    property string{int32} webcam_names [readonly]
    objref Webcam{int32} webcams
end
"""


if __name__ == '__main__':
    main()
