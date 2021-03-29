#Simple example Robot Raconteur camera client
#This program will capture and display
#a s

from RobotRaconteur.Client import *

import cv2, sys, traceback, argparse
import numpy as np


#Function to take the data structure returned from the camera service
#and convert it to an OpenCV array
def ImageToMat(image):

	frame2=image.data.reshape([image.image_info.height, image.image_info.width, int(len(image.data)/(image.image_info.height*image.image_info.width))], order='C')
	
	return frame2

image_consts=None

def main():
	#Accept the names of the webcams and the nodename from command line
	parser = argparse.ArgumentParser(description="RR plug and play client")
	parser.add_argument("--type",type=str,default='rgb',help="type of image")
	args, _ = parser.parse_known_args()

	cam_dict={'rgb':0,'depth':1}

	url='rr+tcp://localhost:59823?service=camera'

	#Connect to the camera
	cam=RRN.ConnectService(url)

	global image_consts
	image_consts = RRN.GetConstants('com.robotraconteur.image', cam)

	# Capture the frame from the camera, returns in raw format
	raw_frame = cam.capture_frame()
	#Convert raw_img to opencv format
	current_frame=ImageToMat(raw_frame)

	cv2.namedWindow("Image")

	cv2.imshow("Image",current_frame)
	cv2.waitKey()
	
	cv2.destroyAllWindows()

	



if __name__ == '__main__':
	main()
