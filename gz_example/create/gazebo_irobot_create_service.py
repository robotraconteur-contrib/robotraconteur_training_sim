# Simulate iRobot Create robot driver

# See the Robot Raconteur Training Simulator https://github.com/robotraconteur-contrib/robotraconteur_training_sim
# for the simulation environment

import RobotRaconteur as RR
#Convenience shorthand to the default node.
#RRN is equivalent to RR.RobotRaconteurNode.s
RRN=RR.RobotRaconteurNode.s
import threading
import sys
import argparse
import numpy as np
import traceback
import time
import drekar_launch_process

# This example currently only implements the "Drive" command

class Create_impl(object):
    def __init__(self):
        self.bump=RR.EventHook()
        self._lock=threading.RLock()

        self._gazebo_server = None
        self._pose_dtype = None
        self._robot_pose = [0,0,0]
        self._omega = 0.0
        self._vel = 0.0
        self._last_t = 0.0
        self._create_state_type = RRN.GetStructureType("experimental.create3.CreateState")

    def drive(self, velocity, radius):
        if abs(radius) <= 0.130:
            self._omega = (velocity/0.130)
            if (radius < 0):
                self._omega = -self._omega
            self._vel = self._omega * radius
        else:
            self._omega = float(velocity)/float(radius)
            self._vel = float(velocity)

    def stop(self):
        self.drive(0,0)

    def _drive_timer_cb(self, timer_evt):
        t = time.perf_counter()
        if self._last_t == 0:
            self._last_t = t
            return
        
        dt = t - self._last_t
        self._last_t = t
            
        
        try:
            res, gazebo_client = self._gazebo_server.TryGetDefaultClient()
            if not res:
                return
            gazebo_world = gazebo_client.get_worlds("default")
            gazebo_create = gazebo_world.get_models("rr_create")
            if self._pose_dtype is None:
                self._pose_dtype = RRN.GetNamedArrayDType('com.robotraconteur.geometry.Pose',gazebo_create)

            self._robot_pose[2] += self._omega * dt
            self._robot_pose[0] += np.cos(self._robot_pose[2]) * (self._vel) * dt
            self._robot_pose[1] += np.sin(self._robot_pose[2]) * (self._vel) * dt

            pose = np.zeros((1,),dtype=self._pose_dtype)
            pose[0]['position']['x'] = self._robot_pose[0]
            pose[0]['position']['y'] = self._robot_pose[1]
            pose[0]['orientation']['w'] = np.cos(self._robot_pose[2]/2.0)
            pose[0]['orientation']['z'] = np.sin(self._robot_pose[2]/2.0)

            gazebo_create.setf_world_pose(pose)

            ret = self._create_state_type()
            ret.time = t

            try:
                self.create_state.OutValue = ret
            except AttributeError:
                pass

        except:
            self._pose_dtype = None
            traceback.print_exc()

    @property
    def distance_traveled(self):
        return -1

    @property
    def angle_traveled(self):
        return -1

    @property
    def bumpers(self):
        return 0
    
    @property
    def play_callback(self):
        return self._play_callback
    @play_callback.setter
    def play_callback(self,value):
        self._play_callback=value

    def claim_play_callback(self):
        pass

    def Init(self, gazebo_url):
        self._gazebo_server = RRN.SubscribeService(gazebo_url)
        
        self._drive_timer = RRN.CreateTimer(0.01,self._drive_timer_cb, False)
        self._drive_timer.Start()


def main():

    #Accept the names of the nodename and port from command line
    parser = argparse.ArgumentParser(description="Example Robot Raconteur iRobot Create service")    
    parser.add_argument("--gazebo-url",type=str,
        default="rr+tcp://localhost:11346/?service=GazeboServer",
        help="The URL for the Gazebo plugin. Default 'rr+tcp://localhost:11346/?service=GazeboServer'")
    args, _ = parser.parse_known_args()

    RRN.RegisterServiceType(_robdef)

    #Initialize the object in the service
    obj=Create_impl()
   
    with RR.ServerNodeSetup("experimental.create3",22354,argv=sys.argv):
    
        #Register the service type and the service
        RRN.RegisterService("create","experimental.create3.Create",obj)

        obj.Init(args.gazebo_url)
    
        drekar_launch_process.wait_exit()
    
_robdef = \
"""

#Service to provide sample interface to the iRobot Create
#This example is for the original iRobot Create using the serial Open Interface (OI) protocol
service experimental.create3

stdver 0.10

enum CreateStateFlags
	unknown = 0,
	bump_right = 0x1,
	bump_left = 0x2,
	wheel_drop_right = 0x4,
	wheel_drop_left = 0x8,
	wheel_drop_caster = 0x10,
	wall_sensor = 0x20,
	cliff_left = 0x40,
	cliff_front_left = 0x80,
	cliff_front_right = 0x100,
	cliff_right = 0x200,
	virtual_wall = 0x400,
	play_button = 0x800,
	advance_button = 0x1000,
	error = 0x800000
end

struct CreateState
	field double time
	field uint32 create_state_flags
	field double velocity
	field double radius
	field double right_wheel_velocity
	field double left_wheel_velocity
	field double distance_traveled
	field double angle_traveled
	field double battery_charge
	field double battery_capacity
end

object Create
	constant double DRIVE_STRAIGHT 32.767
	constant double SPIN_CLOCKWISE -1e-3
	constant double SPIN_COUNTERCLOCKWISE 1e-3

	function void drive(double velocity, double radius)
	function void drive_direct(double right_wheel_velocity, double left_wheel_velocity)
	function void stop()
	function void setf_leds(bool play, bool advance)

	property double distance_traveled [readonly]
	property double angle_traveled [readonly]
	property uint8 bumpers [readonly]

	event bump()

	wire CreateState create_state [readonly]

	# Callback to be called when the play button is pressed
	# claim_play_callback() will assign the current client as the target for the callback
	# Practical implementations will likely want to use a more sophisticated mechanism to assign the callback
	function void claim_play_callback()
	callback uint8[] play_callback(double distance_traveled, double angle_traveled)
end
"""

if __name__ == '__main__':
    main()