#!/usr/bin/env python3

from RobotRaconteur.Client import *
import math
import numpy as np
import time
import yaml
from pathlib import Path
import os

import sys
print(str(Path(os.path.realpath(__file__)).parent.parent.joinpath("toolbox")))
sys.path.append(str(Path(os.path.realpath(__file__)).parent.parent.joinpath("toolbox")))
from general_robotics_toolbox import R2q,rot	#convert R to quaternion

from ur5e1_ik import inv

model_dir = Path(os.path.realpath(__file__)).parent.parent.joinpath("models")

server=RRN.ConnectService('rr+tcp://localhost:11346/?service=GazeboServer')
w=server.get_worlds(str(server.world_names[0]))
pose_dtype = RRN.GetNamedArrayDType("com.robotraconteur.geometry.Pose", server)

def decomp(H):
	return R2q(H[:3,:3]),H[:3,3]

def initialize(robot_sdf,model_name,H):
	q,d=decomp(H)
	model_pose = np.zeros((1,), dtype = pose_dtype)
	model_pose["orientation"]['w'] = q[0]
	model_pose["orientation"]['x'] = q[1]
	model_pose["orientation"]['y'] = q[2]
	model_pose["orientation"]['z'] = q[3]
	model_pose["position"]['x']=d[0]
	model_pose["position"]['y']=d[1]
	model_pose["position"]['z']=d[2]
	w.insert_model(robot_sdf, model_name, model_pose)

def initialize_robot_controller(m):
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
		pass

#model name: ur, sawyer, abb,staubli
#read sdf file
model_name="ur5e1"
f = open(model_dir.joinpath('ur5e/model.sdf'),'r')
robot_sdf = f.read()
with open('calibration/ur5e1.yaml') as file:
	H = np.array(yaml.load(file, Loader=yaml.FullLoader)['H'],dtype=np.float64)
initialize(robot_sdf,model_name,H)
initialize_robot_controller(w.get_models(model_name))

#ur5e1_model = w.get_models("ur5e1")
#kin_controller = 

#read sdf file
model_name="ur5e2"
f = open(model_dir.joinpath('ur5e/model.sdf'),'r')
robot_sdf = f.read()
with open('calibration/ur5e2.yaml') as file:
	H = np.array(yaml.load(file, Loader=yaml.FullLoader)['H'],dtype=np.float64)
initialize(robot_sdf,model_name,H)

initialize_robot_controller(w.get_models(model_name))


box1=[-0.6, 0.6]
box2=[0.6, 0.6]
#read sdf file
model_name="round_bottle"
f = open(model_dir.joinpath(model_name+'/model.sdf'),'r')
model_sdf = f.read()
H=np.eye(4)
H[2][-1]=1.2
for i in range(2):
	H[0][-1]=box1[0]-0.05
	H[1][-1]=box1[1]-0.15+0.1*i
	initialize(model_sdf,model_name+str(2*i),H)
	H[0][-1]=box1[0]+0.05
	H[1][-1]=box1[1]-0.15+0.1*i
	initialize(model_sdf,model_name+str(2*i+1),H)

#read sdf file
model_name="cube200"
f = open(model_dir.joinpath(model_name+'/model.sdf'),'r')
model_sdf = f.read()
H=np.eye(4)
H[2][-1]=1.2
for i in range(2):
	H[0][-1]=box1[0]-0.05
	H[1][-1]=box1[1]-0.15+0.1*(i+2)
	initialize(model_sdf,model_name+str(2*i),H)
	H[0][-1]=box1[0]+0.05
	H[1][-1]=box1[1]-0.15+0.1*(i+2)
	initialize(model_sdf,model_name+str(2*i+1),H)


#read sdf file
model_name="perfume"
f = open(model_dir.joinpath(model_name+'/model.sdf'),'r')
model_sdf = f.read()
H=np.eye(4)
H[2][-1]=1.1
for i in range(2):
	H[0][-1]=box2[0]-0.05
	H[1][-1]=box2[1]-0.15+0.1*i
	initialize(model_sdf,model_name+str(2*i),H)
	H[0][-1]=box2[0]+0.05
	H[1][-1]=box2[1]-0.15+0.1*i
	initialize(model_sdf,model_name+str(2*i+1),H)

#read sdf file
model_name="cube201"
f = open(model_dir.joinpath(model_name+'/model.sdf'),'r')
model_sdf = f.read()
H=np.eye(4)
H[2][-1]=1.1
for i in range(2):
	H[0][-1]=box2[0]-0.05
	H[1][-1]=box2[1]-0.15+0.1*(i+2)
	initialize(model_sdf,model_name+str(2*i),H)
	H[0][-1]=box2[0]+0.05
	H[1][-1]=box2[1]-0.15+0.1*(i+2)
	initialize(model_sdf,model_name+str(2*i+1),H)


#Load landmark
model_name="landmark"
f = open(model_dir.joinpath(model_name+'/model.sdf'),'r')
model_sdf = f.read()

H=np.eye(4)
H[0][-1]=0.2
H[1][-1]=-0.55
H[2][-1]=1.025
H[0:3,0:3] = rot([1,0,0],np.pi)
initialize(model_sdf,model_name,H)

#Load Charuco target
# model_name="charuco_target"
# f = open(model_dir.joinpath(model_name+'/model.sdf'),'r')
# model_sdf = f.read()

# H=np.eye(4)
# H[0][-1]=0.1055
# H[1][-1]=-0.7025
# H[2][-1]=1.025
# #H[0:3,0:3] = rot([1,0,0],np.pi)
# initialize(model_sdf,model_name,H)


print("Done!")

