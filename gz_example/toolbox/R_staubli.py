import numpy as np
def R_ee(angle):
	R=np.array([[-np.cos(angle), -np.sin(angle),0],
				[-np.sin(angle),np.cos(angle) , 0],
				[0,0,-1]])
	return R