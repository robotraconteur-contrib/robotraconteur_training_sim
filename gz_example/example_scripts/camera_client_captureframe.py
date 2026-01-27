#Simple example Robot Raconteur camera client
#This program will capture and display
#a s

from RobotRaconteur.Client import *
from RobotRaconteurCompanion.Util.ImageUtil import ImageUtil

import cv2, sys, traceback, argparse
import numpy as np


def main():
	#Accept the names of the webcams and the nodename from command line
	#parser = argparse.ArgumentParser(description="RR plug and play client")
	
	#args, _ = parser.parse_known_args()

	url='rr+tcp://localhost:59823?service=camera'

	#Connect to the camera
	cam=RRN.ConnectService(url)

	# Use companion util to decode images
	img_util = ImageUtil(client_obj=cam)

	# Capture the frame from the camera, returns in raw format
	raw_frame = cam.capture_frame()
	#Convert raw_img to opencv format
	current_frame=img_util.image_to_array(raw_frame)

	cv2.namedWindow("Image")

	cv2.imshow("Image",current_frame)
	cv2.waitKey()
	
	cv2.destroyAllWindows()

	



if __name__ == '__main__':
	main()
