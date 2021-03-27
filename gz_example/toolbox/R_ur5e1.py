import numpy as np 

def R_ee(angle):
	R=np.array([[np.cos(angle), 0,np.sin(angle)],
				[np.sin(angle), 0, -np.cos(angle)],
				[0,1,0]])
	return R