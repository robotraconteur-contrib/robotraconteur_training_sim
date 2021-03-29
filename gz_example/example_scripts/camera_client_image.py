#Simple example Robot Raconteur webcam client
#This program will show a live streamed image from
#the camera. 

from RobotRaconteur.Client import *

import cv2, sys, traceback, argparse
import numpy as np
import traceback


#Function to take the data structure returned from the Webcam service
#and convert it to an OpenCV array
def ImageToMat(image):
	
	frame2=image.data.reshape([image.image_info.height, image.image_info.width, int(len(image.data)/(image.image_info.height*image.image_info.width))], order='C')
	
	return frame2

image_consts=None
current_frame=None
#This function is called when a new pipe packet arrives
def new_frame(pipe_ep):
	global current_frame

	#Loop to get the newest frame
	while (pipe_ep.Available > 0):
		#Receive the packet
		
		image=pipe_ep.ReceivePacket()
		#Convert the packet to an image and set the global variable
		current_frame=ImageToMat(image)

		return

def main():
	#Accept the names of the camera and the nodename from command line
	parser = argparse.ArgumentParser(description="RR plug and play client")
	parser.add_argument("--type",type=str,default='rgb',help="type of image")
	args, _ = parser.parse_known_args()

	cam_dict={'rgb':0,'depth':1}

	url='rr+tcp://localhost:59823?service=camera'

	#Connect to the camera
	cam=RRN.ConnectService(url)

	global image_consts
	image_consts = RRN.GetConstants('com.robotraconteur.image', cam)

	#Connect the pipe FrameStream to get the PipeEndpoint p	
	
	p=cam.frame_stream.Connect(-1)

	#Set the callback for when a new pipe packet is received to the
	#new_frame function
	p.PacketReceivedEvent+=new_frame


	try:
		cam.start_streaming()
	except: 
		traceback.print_exc()
		pass

	cv2.namedWindow("Image")

	while True:
		#Just loop resetting the frame
		#This is not ideal but good enough for demonstration

		if (not current_frame is None):

			cv2.imshow("Image",current_frame)
		if cv2.waitKey(50)!=-1:
			break
	cv2.destroyAllWindows()

	p.Close()
	cam.stop_streaming()



if __name__ == '__main__':
	main()
