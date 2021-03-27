from general_robotics_toolbox import *
from viscid import rotm2eul, eul2rotm
from qpsolvers import solve_qp
from scipy.optimize import fminbound

ex=np.array([[1],[0],[0]])
ey=np.array([[0],[1],[0]])
ez=np.array([[0],[0],[1]])


H=np.concatenate((ez,ey,ex,ey,ex,ey,ex),axis=1)
p0=np.array([[0],[0],[0]])
p1=np.array([[0.081],[0],[0.317]])
p2=np.array([[0.],[0.1925],[0]])
p3=np.array([[0.4],[0],[0]])
p4=np.array([[0],[-0.1685],[0]])
p5=np.array([[0.4],[0],[0]])
p6=np.array([[0],[0.1363],[0]])
p7=np.array([[0.13375],[0],[0]])

P=np.concatenate((p0,p1,p2,p3,p4,p5,p6,p7),axis=1)
joint_type=np.zeros(7)
Sawyer_def=Robot(H,P,joint_type)

def threshold(theta):
    if theta>np.pi:
        theta-=2*np.pi
    elif theta<-np.pi:
        theta+=2*np.pi
    return theta

def min_alpha(a,q_cur,qdot_star,robot,R,p,w,Kp):
    Sawyer_pose=fwdkin(Sawyer_def,q_cur+a*qdot_star.reshape((7,1)))
    R_next=Sawyer_pose.R
    p_next=Sawyer_pose.p
    ER=np.dot(R_next,np.transpose(R))
    axang = rotm2axang(ER)
    theta=axang[3]                     #decompose ER to (k,theta) pair
    eR=2*(1-np.cos(theta/2));
    alpha=np.dot(np.transpose(p_next-p),np.dot(Kp,(p_next-p)))+np.dot(w,eR)

def fwd(q):
    return fwdkin(Sawyer_def,q)

def inv(pd,Rd=np.array([[ 0., 0., -1. ],[ 0., -1.,  0.],[-1.,  0., 0.]]),q_cur=np.array([0.41542578, -1.12959277,  0.03109668,  2.16097559, -0.06389746,  0.52792773,  2.35849512]).reshape((7,1))):

    w=10000             #set the weight between orientation and position
    Kq=.01*np.eye(7)    #small value to make sure positive definite
    Kp=np.eye(3)
    KR=np.eye(3)        #gains for position and orientation error
    steps=20           #number of steps to take to get to desired destination

    # bounding
    # G=np.vstack([-np.eye(7),np.eye(7)])
    # lb=np.array([])
    # ub=np.array([])
    # h=np.vstack([-lb,ub])


    for i in range(steps):
    #     get current H and J
        Sawyer_pose=fwdkin(Sawyer_def,q_cur)
        R_cur=Sawyer_pose.R
        p_cur=Sawyer_pose.p
        J0T=robotjacobian(Sawyer_def,q_cur)     #calculate current Jacobian
        Jp=J0T[3:,:]
        JR=J0T[:3,:]                      #decompose to position and orientation Jacobian

        ER=np.dot(R_cur,np.transpose(Rd))
        EP=p_cur-pd                         #error in position and orientation

        k,theta = R2rot(ER)             #decompose ER to (k,theta) pair               #decompose ER to (k,theta) pair
        phi=rotm2eul(ER,'ZYX')
        Rz=eul2rotm([phi[0], 0, 0],'ZYX')
        Ry=eul2rotm([0, phi[1], 0],'ZYX')    #decompose ER to Euler Angles
        temp=np.hstack((ez,ey,np.dot(Ry,ex)))

        J_phi_inv=np.dot(Rz,temp)
        J_phi=np.linalg.inv(J_phi_inv)               #calculate Jacobian for Euler angle representation

    #     set up s for different norm for ER

        # s=2*np.dot(k,np.sin(theta))         #eR1
        s=np.sin(theta/2)*k         #eR2
        # s=2*theta*k              #eR3
        # s=np.dot(J_phi,phi)              #eR4
        
        vd=-np.dot(Kp,EP)
        wd=-np.dot(KR,s)          
        H=np.dot(np.transpose(Jp),Jp)+w*np.dot(np.transpose(JR),JR)+Kq 
        H=(H+np.transpose(H))/2

        f=-np.dot(np.transpose(Jp),vd)-w*np.dot(np.transpose(JR),wd)               #setup quadprog parameters

    #     quadratic function with +/-qddot (1 rad/s^2) as upper/lower bound 

        qdot_star=solve_qp(H, f)
    #     find best step size to take
        # alpha=fminbound(min_alpha,0,1,args=(q_cur,qdot_star,Sawyer_def,Rd,pd,w,Kp))
        alpha=0.8
        q_cur=q_cur+alpha*qdot_star.reshape((7,1))
        # print(2*(1-np.cos(theta)))              #orientation error
        # print(ER)
    #check if reached

    EP=p_cur-pd 
    if np.linalg.norm(EP)>0.05:
        raise UnboundLocalError("Out of Workspace")
    q_cur[-1]=threshold(q_cur[-1])
    return q_cur.reshape(7)

# Rd=np.array([[ 0., 0., -1. ],
#  [ 0., -1.,  0.],
#  [-1.,  0., 0.]])


# q=ik(Rd,[0.5,0.3,0.4])
# print(fwd(q))