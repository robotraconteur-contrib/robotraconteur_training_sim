from tesseract.tesseract_scene_graph import SimpleResourceLocator, SimpleResourceLocatorFn
from tesseract.tesseract_environment import Environment
from tesseract.tesseract_common import FilesystemPath, Isometry3d, Translation3d, Quaterniond, CollisionMarginData
from tesseract.tesseract_collision import ContactResultMap, ContactRequest, ContactTestType_ALL, ContactResultVector
from tesseract.tesseract_collision import flattenResults as collisionFlattenResults
import os
import re
import traceback
from tesseract_viewer import TesseractViewer
import numpy as np
import time
import sys
import yaml
sys.path.append('../toolbox/')
from gazebo_model_resource_locator import GazeboModelResourceLocator

######tesseract environment setup:
t_env = Environment()
urdf_path = FilesystemPath("combined.urdf")
srdf_path = FilesystemPath("combined.srdf")
assert t_env.init(urdf_path, srdf_path, GazeboModelResourceLocator())

viewer = TesseractViewer()

viewer.update_environment(t_env, [0,0,0])

#link and joint names in urdf
ur5e1_joint_names=["ur5e1__shoulder_pan_joint","ur5e1__shoulder_lift_joint","ur5e1__elbow_joint","ur5e1__wrist_1_joint","ur5e1__wrist_2_joint","ur5e1__wrist_3_joint"]
ur5e2_joint_names=["ur5e2__shoulder_pan_joint","ur5e2__shoulder_lift_joint","ur5e2__elbow_joint","ur5e2__wrist_1_joint","ur5e2__wrist_2_joint","ur5e2__wrist_3_joint"]


robot_joint_list=[ur5e1_joint_names,ur5e2_joint_names]
num_robot=len(robot_joint_list)

viewer.start_serve_background()





with open('../calibration/ur5e1.yaml') as file:
	H_ur5e1 		= np.array(yaml.load(file)['H'],dtype=np.float64)
with open('../calibration/ur5e2.yaml') as file:
	H_ur5e2		= np.array(yaml.load(file)['H'],dtype=np.float64)


#update robot poses based on calibration file
t_env.changeJointOrigin("abb1_pose", Isometry3d(H_ur5e1))
t_env.changeJointOrigin("abb2_pose", Isometry3d(H_ur5e2))


for i in range(num_robot):
	t_env.setState(robot_joint_list[i], np.zeros(len(robot_joint_list[i])))


time.sleep(1)
viewer.update_environment(t_env, [0,0,0])


if sys.version_info[0] < 3:
    raw_input("press enter")
else:
    input("press enter")