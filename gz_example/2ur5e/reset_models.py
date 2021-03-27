#!/usr/bin/env python3
#reset objects and box location to random
import numpy as np
from RobotRaconteur.Client import *
import sys
sys.path.append('../../toolbox/')
from general_robotics_toolbox import R2q	#convert R to quaternion

server=RRN.ConnectService('rr+tcp://localhost:11346/?service=GazeboServer')
w=server.get_worlds(str(server.world_names[0]))
pose_dtype = RRN.GetNamedArrayDType("com.robotraconteur.geometry.Pose", server)
def decomp(H):
	return R2q(H[:3,:3]),H[:3,3]

def reset(name,H):
	element = w.get_models(name)	
	q,d=decomp(H)
	model_pose = np.zeros((1,), dtype = pose_dtype)
	model_pose["orientation"]['w'] = q[0]
	model_pose["orientation"]['x'] = q[1]
	model_pose["orientation"]['y'] = q[2]
	model_pose["orientation"]['z'] = q[3]
	model_pose["position"]['x']=d[0]
	model_pose["position"]['y']=d[1]
	model_pose["position"]['z']=d[2]
	element.setf_world_pose(model_pose)


box1=[-0.6, 0.6]
box2=[0.6, 0.6]
#read sdf file
model_name="round_bottle"

H=np.eye(4)
H[2][-1]=1.2
for i in range(4):
	H[0][-1]=box1[0]-0.05
	H[1][-1]=box1[1]-0.15+0.1*i
	reset(model_name+str(2*i),H)
	H[0][-1]=box1[0]+0.05
	H[1][-1]=box1[1]-0.15+0.1*i
	reset(model_name+str(2*i+1),H)


#read sdf file
model_name="perfume"
H=np.eye(4)
H[2][-1]=1.1
for i in range(4):
	H[0][-1]=box2[0]-0.05
	H[1][-1]=box2[1]-0.15+0.1*i
	reset(model_name+str(2*i),H)
	H[0][-1]=box2[0]+0.05
	H[1][-1]=box2[1]-0.15+0.1*i
	reset(model_name+str(2*i+1),H)

