#Simple example Robot Raconteur webcam client
#This program will show a live streamed image from
#the camera. 

from RobotRaconteur.Client import *

import cv2, sys, traceback, argparse
import numpy as np
import traceback
import time
import threading


#Function to take the data structure returned from the Webcam service
#and convert it to an OpenCV array
def CompressedImageToMat(compressed_image):

	frame2 = cv2.imdecode(compressed_image.data,1)
	
	return frame2

image_consts=None
current_compressed_frame=None
new_frame_lock = threading.Lock()

#This function is called when a new pipe packet arrives
def new_frame(pipe_ep):

	global current_compressed_frame
	with new_frame_lock:

		#Loop to get the newest frame
		while (pipe_ep.Available > 0):
			#Receive the packet
			
			compressed_image=pipe_ep.ReceivePacket()
		#Convert the packet to an image and set the global variable
		current_compressed_frame=compressed_image

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
	
	p=cam.preview_stream.Connect(-1)

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

		if (not current_compressed_frame is None):
			current_frame = CompressedImageToMat(current_compressed_frame)

			cv2.imshow("Image",current_frame)
		if cv2.waitKey(20)!=-1:
			break
	cv2.destroyAllWindows()

	p.Close()
	cam.stop_streaming()



if __name__ == '__main__':
	main()
