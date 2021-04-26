#!/usr/bin/env python3

from RobotRaconteur.Client import *
import math
import numpy as np
import time
import yaml
from pathlib import Path
import os
import traceback

import sys
print(str(Path(os.path.realpath(__file__)).parent.parent.joinpath("toolbox")))
sys.path.append(str(Path(os.path.realpath(__file__)).parent.parent.joinpath("toolbox")))
from general_robotics_toolbox import R2q,rot	#convert R to quaternion

from ur5e1_ik import inv

model_dir = Path(os.path.realpath(__file__)).parent.parent.joinpath("models")

server=RRN.ConnectService('rr+tcp://localhost:11346/?service=GazeboServer')
w=server.get_worlds(str(server.world_names[0]))

def init_robot_controller(m):
	try:
		m.destroy_kinematic_joint_controller()
		m.create_kinematic_joint_controller()
		m_controller = m.get_kinematic_joint_controller()	
		j_pos = [0.0,-np.pi/2,0.0,0.0,0.0,0.0]
		j_names = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]
		for j in j_names:
			m_controller.add_joint(j)
		j_command = {j_names[i]: j_pos[i] for i in range(6)}
		m_controller.joint_position_command.PokeOutValue(j_command)
	except:
		traceback.print_exc()

ur5e1_model = w.get_models("ur5e1")
init_robot_controller(ur5e1_model)
	




