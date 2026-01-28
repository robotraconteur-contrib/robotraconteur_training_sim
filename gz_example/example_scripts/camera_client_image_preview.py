#Simple example Robot Raconteur webcam client
#This program will show a live streamed image from
#the camera. 

from RobotRaconteur.Client import *
from RobotRaconteurCompanion.Util.ImageUtil import ImageUtil

import cv2, sys, traceback, argparse
import numpy as np
import traceback
import time
import threading


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

	# Use companion util to decode images
	img_util = ImageUtil(client_obj=cam)

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
			current_frame = img_util.compressed_image_to_array(current_compressed_frame)

			cv2.imshow("Image",current_frame)
		if cv2.waitKey(20)!=-1:
			break
	cv2.destroyAllWindows()

	p.Close()
	cam.stop_streaming()



if __name__ == '__main__':
	main()
