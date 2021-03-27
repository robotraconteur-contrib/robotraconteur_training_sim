from math import *
import numpy as np

def threshold(theta):
	if theta>np.pi:
		theta-=2*np.pi
	elif theta<-np.pi:
		theta+=2*np.pi
	return theta
def inv(p,R=np.array([[-1,0,0],[0,0,-1],[0,-1,0]])):
	yaw_WgripDegree=-90
	orientation=atan2(-R[1][0],-R[1][2])
	orientation=np.degrees(orientation)
	
	xWgrip=p[0]
	yWgrip=p[1]
	zWgrip=p[2] 
	d1 = 0.089159 
	d2 = d3 = 0
	d4 = 0.10915
	d5 = 0.09465
	d6 = 0.0823

	a1 = a4 = a5 = a6 = 0
	a2 = 0.425
	a3 = 0.39225


  # step 1: get xgrip, ygrip, zgrip
  # Ogrip=H(base->world)*Owgrip
  # a 30*30*1.6 cm base for the robot
	xgrip = -xWgrip
	ygrip = -yWgrip
	zgrip = zWgrip


  # step 2: get xcen, ycen, zcen 
	xcen=xgrip+a6*sin((yaw_WgripDegree-90)*pi/180.0)
	ycen=ygrip-a6*cos((yaw_WgripDegree-90)*pi/180.0)
	zcen=zgrip

	# step 3: get theta 1 in radians !!
	theta1 = (atan2(ycen,xcen)-atan2(0.11,sqrt(xcen*xcen+ycen*ycen-0.11*0.11)))#asin( (d2-(abs(d3)-d4)) / sqrt(xcen*xcen+ycen*ycen) )

  # step 4: get theta 6 in radians
	theta6 = (theta1*180.0/pi-yaw_WgripDegree-orientation)*pi/180.0
 
  # step 5: get x3end, y3end, z3end

	x3end = xcen+0.11*sin(theta1)-0.083*cos(theta1)
	y3end = ycen-0.11*cos(theta1)-0.083*sin(theta1)
	z3end = zcen+0.138

	# step 6: get theta2, theta 3, theta 4 in radians
	w=sqrt(x3end*x3end+y3end*y3end)
	s=z3end-d1
	D=(s*s+w*w-a2*a2-a3*a3)*1.0/(2*a2*a3)
 

	theta3= atan2(+sqrt(1-D*D),D) #elbow up !!!!!
	beta=atan2(a3*sin(theta3),a2+a3*cos(theta3))
	gamma=atan2(s,w)
	theta2= -gamma-beta
	theta4= -(theta3-beta-gamma)-pi/2


	theta5=-pi/2  # fixed value
	theta1+=np.pi #only for simulation
	theta1=threshold(theta1)
	theta6=threshold(theta6)
	q=np.array([theta1,theta2,theta3,theta4,theta5,theta6])
	if np.array_equal(R,[[1,0,0],[0,1,0],[0,0,1]]):
		q=np.array([theta1,theta2,theta3,theta4,0,0])
	return(q)

