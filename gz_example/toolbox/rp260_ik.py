from general_robotics_toolbox import *
from general_robotics_toolbox_invkin import *


ex=np.array([[1],[0],[0]])
ey=np.array([[0],[1],[0]])
ez=np.array([[0],[0],[1]])


H=np.concatenate((ez,ey,ey,ex,ey,ex),axis=1)
p0=np.array([[0],[0],[0.3302]])
p1=np.array([[0],[0],[0]])
p2=np.array([[0.19812],[-0.12446],[-0.01905]])
p3=np.array([[0.2032],[0],[0.]])
p4=np.array([[0.],[0],[0]])
p5=np.array([[0.0635],[0],[0]])
p6=np.array([[0],[0],[0]])
P=np.concatenate((p0,p1,p2,p3,p4,p5,p6),axis=1)
joint_type=np.zeros(6)
upper_limit=np.array([3.49065850399,1.308996939,2.53072741539,6.28318530718,2.09439510239,1.57079632679])
lowerer_limit=np.array([-1.57079632679,-4.18879020479,-2.53072741539,-3.2288591161,-2.09439510239,-6.28318530718])
rp260_def=Robot(H,P,joint_type,joint_lower_limit = lowerer_limit, joint_upper_limit = upper_limit)
def fwd(q):
    return fwdkin(rp260_def,q)

def inv(p,R=np.array([[0,0,1],[0,1,0],[-1,0,0]])):
	pose=Transform(R,p)
	q_all=robot6_sphericalwrist_invkin(rp260_def,pose)
	for q in q_all:
		if q[1]<0 and q[1]>-1.57 and q[2]>0 and q[4]>0:
			return q
	return q
