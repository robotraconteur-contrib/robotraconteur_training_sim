import numpy as np

def train(objects, desired_location):
	Q=np.inf(2,len(objects),len(desired_location))