import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import RobotRaconteurCompanion as RRC
from RobotRaconteurCompanion.Util.InfoFileLoader import InfoFileLoader
from RobotRaconteurCompanion.Util.AttributesUtil import AttributesUtil
import sys
import argparse
import traceback
import threading
import re

class Gripper_impl:
    def __init__(self, tool_info, gazebo_parent_link, gazebo_contact_sensor, payload_prefix):
        self._lock = threading.Lock()
        self.tool_info = tool_info
        self.device_info = tool_info.device_info
        self.gazebo_parent_link=gazebo_parent_link
        self.gazebo_contact_sensor=gazebo_contact_sensor
        self.payload_prefix = payload_prefix
        self.current_model = None
        self.current_link = None

    def open(self):
        with self._lock:
            if self.current_model is not None and self.current_link is not None:
                try:
                    self.gazebo_parent_link.detach_link(self.current_model,self.current_link)
                except:
                    traceback.print_exc()
                finally:
                    self.current_model = None
                    self.current_payload = None

    def close(self):
        with self._lock:
            contacts=self.gazebo_contact_sensor.contacts.PeekInValue()[0]
          
            model_name = None
            link_name = None

            for c in contacts:
                c_name = c.contact_name1

                for p in self.payload_prefix:
                    re_m = re.match(f"^({p}.*)::(\w+)::\w+$",c_name)
                    if re_m:
                        model_name=re_m.group(1)
                        link_name=re_m.group(2)
                        break
                if link_name is not None:
                    break

            if link_name is None:
                return
            
            try:
                self.gazebo_parent_link.attach_link(model_name,link_name)
            except:
                traceback.print_exc()
                return
            
            self.current_model = model_name
            self.current_link = link_name

def main():

    #Accept the names of the nodename and port from command line
    parser = argparse.ArgumentParser(description="Gazebo link attacher gripper service")
    parser.add_argument("--tool-info-file", type=argparse.FileType('r'),default=None,required=True,help="Tool info file for tool (required)")
    parser.add_argument("--gazebo-gripper-link", type=str,help="The Gazebo link that will be used to attach payloads (fully qualified path)")
    parser.add_argument("--gazebo-gripper-contact-sensor", type=str, help="The Gazebo contact sensor that will be used to detect the payload (fully qualified path)")
    parser.add_argument("--gazebo-payload-prefix", type=str, help="Comma separated list of payload name prefixes")
    parser.add_argument("--nodename",type=str,default="org.gazebo.simulation.gripper",help="The NodeName to use")
    parser.add_argument("--tcp-port",type=int,default=52521,help="The listen TCP port")
    parser.add_argument("--wait-signal",action='store_const',const=True,default=False)
    args, _ = parser.parse_known_args()

    
    RRC.RegisterStdRobDefServiceTypes(RRN)
    with args.tool_info_file:
        tool_info_text = args.tool_info_file.read()

    info_loader = InfoFileLoader(RRN)
    tool_info, tool_ident_fd = info_loader.LoadInfoFileFromString(tool_info_text, "com.robotraconteur.robotics.tool.ToolInfo", "device")

    attributes_util = AttributesUtil(RRN)
    device_attributes = attributes_util.GetDefaultServiceAttributesFromDeviceInfo(tool_info.device_info)

    #Initialize the object in the service
    
    
        
    with RR.ServerNodeSetup(args.nodename,args.tcp_port,argv=sys.argv):
        server = RRN.ConnectService('rr+tcp://localhost:11346?service=GazeboServer')
        gripper1_contact_sensor = server.get_sensors("default::" + args.gazebo_gripper_contact_sensor)
        world = server.get_worlds('default')
        gripper_link_path=str(args.gazebo_gripper_link).split("::")
        gripper_parent_model = world.get_models(gripper_link_path[0])
        for i in range(1,len(gripper_link_path)-1):
            gripper_parent_model=gripper_parent_model.get_child_models(gripper_link_path[i])        
        gripper1_link = gripper_parent_model.get_links(gripper_link_path[-1])

        payload_prefix = args.gazebo_payload_prefix.split(",")
        obj=Gripper_impl(tool_info, gripper1_link, gripper1_contact_sensor, payload_prefix)
    
        #Register the service type and the service
        
        ctx = RRN.RegisterService("gripper","com.robotraconteur.robotics.tool.Tool",obj)
        ctx.SetServiceAttributes(device_attributes)

        print("Gripper service started")
    
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
    

if __name__ == '__main__':
    main()
