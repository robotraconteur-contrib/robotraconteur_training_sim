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
from general_robotics_toolbox import R2q	#convert R to quaternion

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

#model name: ur, sawyer, abb,staubli
#read sdf file
model_name="ur5e1"
f = open(model_dir.joinpath('ur5e/model.sdf'),'r')
robot_sdf = f.read()
with open('calibration/ur5e1.yaml') as file:
	H = np.array(yaml.load(file)['H'],dtype=np.float64)
initialize(robot_sdf,model_name,H)
#read sdf file
model_name="ur5e2"
f = open(model_dir.joinpath('ur5e/model.sdf'),'r')
robot_sdf = f.read()
with open('calibration/ur5e2.yaml') as file:
	H = np.array(yaml.load(file)['H'],dtype=np.float64)
initialize(robot_sdf,model_name,H)



box1=[-0.6, 0.6]
box2=[0.6, 0.6]
#read sdf file
model_name="round_bottle"
f = open(model_dir.joinpath(model_name+'/model.sdf'),'r')
model_sdf = f.read()
H=np.eye(4)
H[2][-1]=1.2
for i in range(4):
	H[0][-1]=box1[0]-0.05
	H[1][-1]=box1[1]-0.15+0.1*i
	initialize(model_sdf,model_name+str(2*i),H)
	H[0][-1]=box1[0]+0.05
	H[1][-1]=box1[1]-0.15+0.1*i
	initialize(model_sdf,model_name+str(2*i+1),H)


#read sdf file
model_name="perfume"
f = open(model_dir.joinpath(model_name+'/model.sdf'),'r')
model_sdf = f.read()
H=np.eye(4)
H[2][-1]=1.1
for i in range(4):
	H[0][-1]=box2[0]-0.05
	H[1][-1]=box2[1]-0.15+0.1*i
	initialize(model_sdf,model_name+str(2*i),H)
	H[0][-1]=box2[0]+0.05
	H[1][-1]=box2[1]-0.15+0.1*i
	initialize(model_sdf,model_name+str(2*i+1),H)
    
print("Done!")

