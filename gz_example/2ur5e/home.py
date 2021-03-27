#!/usr/bin/env python3
from RobotRaconteur.Client import *
import time
import numpy as np
import sys

sys.path.append('../toolbox')

robot = RRN.ConnectService('rr+tcp://localhost:52511?service=robot')        #ur5e1
robot3 = RRN.ConnectService('rr+tcp://localhost:52512?service=robot')       #ur5e1


robot_const = RRN.GetConstants("com.robotraconteur.robotics.robot", robot)
halt_mode = robot_const["RobotCommandMode"]["halt"]
jog_mode = robot_const["RobotCommandMode"]["jog"]
robot.command_mode = halt_mode
time.sleep(0.1)
robot.command_mode = jog_mode

robot3.command_mode = halt_mode
time.sleep(0.1)
robot3.command_mode = jog_mode



from ur5e1_ik import inv



p=inv([-0.3,0.0,0.2]).reshape((6,1))
robot.jog_freespace(p, np.ones((6,)), False)
robot3.jog_freespace(p, np.ones((6,)), False)
