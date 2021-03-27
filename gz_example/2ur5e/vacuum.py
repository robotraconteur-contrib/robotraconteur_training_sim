#!/usr/bin/env python3

import numpy as np
import RobotRaconteur as RR
RRN=RR.RobotRaconteurNode.s

import traceback

#vacuum 
import rospy
from gazebo_ros_link_attacher.srv import Attach, AttachRequest, AttachResponse
attach_srv = rospy.ServiceProxy('/link_attacher_node/attach',Attach)
attach_srv.wait_for_service()

detatch_srv = rospy.ServiceProxy('/link_attacher_node/detach',Attach)
detatch_srv.wait_for_service()

class create_impl(object):

	def vacuum(self,robot_name,obj_name,action):

		req = AttachRequest()
		req.model_name_1=robot_name+'::'+'gripper'
		req.link_name_1 = "body"
		req.model_name_2 = obj_name
		req.link_name_2 = "link"
		if action:
			attach_srv.call(req)
		else:
			detatch_srv.call(req)

with RR.ServerNodeSetup("vacuum_Service", 50000) as node_setup:

	RRN.RegisterServiceTypeFromFile("../../robdef/edu.rpi.robotics.vacuumlink")

	vacuum=create_impl()
	RRN.RegisterService("vacuumlink", "edu.rpi.robotics.vacuumlink.vacuumlink", vacuum)
	print("vacuum service started......")
	input("Press enter to quit")
