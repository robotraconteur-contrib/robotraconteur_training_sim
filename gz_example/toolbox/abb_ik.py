from general_robotics_toolbox import *
from general_robotics_toolbox_invkin import *
import numpy as np

ex=np.array([[1],[0],[0]])
ey=np.array([[0],[1],[0]])
ez=np.array([[0],[0],[1]])


H=np.concatenate((ez,ey,ey,ex,ey,ex),axis=1)
p0=np.array([[0],[0],[0.3991]])
p1=np.array([[0],[0],[0]])
p2=np.array([[0.],[0],[0.448]])
p3=np.array([[0],[0],[0.042]])
p4=np.array([[0.451],[0],[0]])
p5=np.array([[0.082],[0],[0]])
p6=np.array([[0],[0],[0]])
P=np.concatenate((p0,p1,p2,p3,p4,p5,p6),axis=1)
joint_type=np.zeros(6)
upper_limit=np.array([2.967,2.269,1.222,4.712,2.269,6.283])
lowerer_limit=np.array([-2.967,-1.745,-3.491,-4.712,-2.269,-6.283])
ABB_def=Robot(H,P,joint_type,joint_lower_limit = lowerer_limit, joint_upper_limit = upper_limit)
def fwd(q):
    return fwdkin(ABB_def,q)

def inv(p,R=np.array([[0,0,1],[0,1,0],[-1,0,0]])):
	pose=Transform(R,p)
	q_all=robot6_sphericalwrist_invkin(ABB_def,pose)
	for q in q_all:
		if q[1]>0 and q[2]>-np.pi/2 and np.abs(q[3])<np.pi/3.:
			return q
	return q
