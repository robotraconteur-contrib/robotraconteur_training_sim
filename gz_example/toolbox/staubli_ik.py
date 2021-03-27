from general_robotics_toolbox import *
from general_robotics_toolbox_invkin import *

ex=np.array([[1],[0],[0]])
ey=np.array([[0],[1],[0]])
ez=np.array([[0],[0],[1]])


H=np.concatenate((ez,ey,ey,ez,ey,ez),axis=1)
p0=np.array([[0],[0],[0]])
p1=np.array([[0],[0],[0.375]])
p2=np.array([[0],[0.02],[0.29]])
p3=np.array([[0.],[0],[0]])
p4=np.array([[0],[0],[0.31]])
p5=np.array([[0],[0],[0.07]])
p6=np.array([[0],[0],[0]])
P=np.concatenate((p0,p1,p2,p3,p4,p5,p6),axis=1)
joint_type=np.zeros(6)
upper_limit=np.radians([180,127.5,142.5,270,132.5,270])
lowerer_limit=np.radians([-180,-127.5,-142.5,-270,-122.5,-270])


Staubli_def=Robot(H,P,joint_type,joint_lower_limit = lowerer_limit, joint_upper_limit = upper_limit)
def fwd(q):
    return fwdkin(Staubli_def,q)

def inv(p,R=np.array([[ -1, 0., 0 ],[ 0., 1,  0.],[0,  0., -1]])):
	pose=Transform(R,p)
	q_all=robot6_sphericalwrist_invkin(Staubli_def,pose)
	for q in q_all:
		if q[1]>0 and q[2]>0 and q[4]>0:
			return q
	return q
