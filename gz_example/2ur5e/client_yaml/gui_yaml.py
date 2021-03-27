#!/usr/bin/python3
from RobotRaconteur.Client import *
import sys, os, time, yaml, traceback
from tkinter import *
from tkinter import messagebox
import numpy as np

cwd = os.getcwd()
#register robot service definition
directory='/home/iamnotedible/catkin_ws/src/robotraconteur_companion/robdef/group1/'
os.chdir(directory)
RRN.RegisterServiceTypesFromFiles(['com.robotraconteur.robotics.robot.robdef'],True)
os.chdir(cwd)

#register service constant
robot_const = RRN.GetConstants("com.robotraconteur.robotics.robot")
state_flags_enum = robot_const['RobotStateFlags']


#connection failed callback
def connect_failed(s, client_id, url, err):
	# print ("Client connect failed: " + str(client_id.NodeID) + " url: " + str(url) + " error: " + str(err))
	for name in robot_namelist:
		if name in url[0]:
			plug[name].config(relief="raised")
			plug[name].configure(bg='red')

def multisplit(s, delims):
	pos = 0
	for i, c in enumerate(s):
		if c in delims:
			yield s[pos:i]
			pos = i + 1
	yield s[pos:]


top=Tk()

def create_robot_yaml(name):
	yaml_dict={'robot_name':name,
	'robot_command':robot_command[name].get(),
	'height':float(height[name].get()),
	'home':list(map(float,filter(None,multisplit(home[name].get(),',')))),
	'calibration_speed':float(calibration_speed[name].get()),
	'calibration_start':list(map(float,filter(None,multisplit(calibration_start[name].get(),',')))),
	'calibration_R':list(map(float,filter(None,multisplit(calibration_R[name].get(),',')))),
	'obj_namelists':list(filter(None,multisplit(obj_namelists[name].get(),','))),
	'pick_height':float(pick_height[name].get()),
	'place_height':float(place_height[name].get()),
	'tag_position':float(tag_position[name].get()),
	'gripper_orientation':float(gripper_orientation[name].get()),
	'url':url[name].get(),
	'tool_url':tool_url[name].get()}
	with open(r'client_'+name+'.yaml', 'w') as file:
		yaml.dump(yaml_dict, file)
	messagebox.showinfo(title=None, message=name+' yaml created!')
	return

def gripper_ctrl(name):
	if gripper[name].config('relief')[-1] == 'sunken':
		gripper[name].config(relief="raised")
		gripper[name].configure(bg='red')
		gripper[name].configure(text='gripper off')
		tool_client[name].open()

	else:
		gripper[name].config(relief="sunken")
		gripper[name].configure(bg='green')
		gripper[name].configure(text='gripper on')
		tool_client[name].close()
	return

def plug_robot(name):

	if plug[name].config('relief')[-1] == 'sunken':
		plug[name].config(relief="raised")
		plug[name].configure(bg='red')
	else:
		plug[name].config(relief="sunken")
		plug[name].configure(bg='green')
	return

def calibrate_robot(name):
	if state_w[name].TryGetInValue()[0]:
		try:
			os.system("python3 ../calibration/calibration_auto.py --robot-name="+name)
			messagebox.showinfo(title=None, message='calibration finished!')
		except:
			messagebox.showinfo(title=None, message=(traceback.print_exc()))
	else:
		messagebox.showwarning(title=None, message=name+' service not running!')
	return

def startjob(name):
	if plug[name].config('relief')[-1] == 'raised':
		messagebox.showinfo(title=None, message='plug in '+name+' first!')
		return
	os.system("python3 ../client_same.py --robot-name="+name)

def discover_service(name):
	res=RRN.FindServiceByType("com.robotraconteur.robotics.robot.Robot",
	["rr+local","rr+tcp","rrs+tcp"])

	for serviceinfo2 in res:
		if name in serviceinfo2.NodeName:
			url[name].delete(0, END)
			url[name].insert(0, serviceinfo2.ConnectionURL[0])
			robot_sub[name]=RRN.SubscribeService(serviceinfo2.ConnectionURL[0])
			robot_sub[name].ClientConnectFailed+= connect_failed
			state_w[name] = robot_sub[name].SubscribeWire("robot_state")
			messagebox.showinfo(title=None, message=name+' found, url and subscription updated!')
			return
	#if not returned with found
	messagebox.showwarning(title=None, message=name+' not found!')

def moveaway(name):
	temp=100*np.random.random()
	H_temp=[[1,0,0,temp],[0,1,0,temp],[0,0,1,temp],[0,0,0,1]]
	with open(r'../calibration/'+name+'.yaml', 'w') as file:
		yaml.dump({'H':H_temp}, file)
	messagebox.showinfo(title=None, message=name+' moved away in calibration file!')
##RR part
def update_label(name):
		robot_state=state_w[name].TryGetInValue()
		flags_text[name] = "Robot State Flags:\n\n"
		if robot_state[0]:
			for flag_name, flag_code in state_flags_enum.items():
				if flag_code & robot_state[1].robot_state_flags != 0:
					flags_text[name] += flag_name + "\n"
		else:
			flags_text[name] += 'service not running'
		label[name].config(text = flags_text[name])
		label[name].after(500, lambda: update_label(name))

def update_cognex():
	wire_value=detection_wire.TryGetInValue()
	if wire_value[0]:
		cognex_status.configure(bg='green')
	else:
		cognex_status.configure(bg='red')
	cognex_status.after(500,update_cognex)


robot_namelist=['sawyer','ur','abb']
#GUI field element dict
robot_name={}
robot_command={}
height={}
home={}
calibration_speed={}
calibration_start={}
calibration_R={}
obj_namelists={}
pick_height={}
place_height={}
gripper_orientation={}
tag_position={}
url={}
tool_url={}
#GUI button element dict
create={}
plug={}
gripper={}
calibrate={}
move_away={}
start_job={}
#RR robot dict
robot_sub={}
tool_client={}
state_w={}
flags_text={}
label={}
discover={}

for i in range(len(robot_namelist)):
	Label(top, text="Robot Name").grid(row=0,column=2*i)
	Label(top, text="Robot Command").grid(row=1,column=2*i)
	Label(top, text="Robot Height").grid(row=2,column=2*i)
	Label(top, text="Home Position").grid(row=3,column=2*i)
	Label(top, text="Calibration Speed").grid(row=4,column=2*i)
	Label(top, text="Calibration Start").grid(row=5,column=2*i)
	Label(top, text="Calibration Orientation").grid(row=6,column=2*i)
	Label(top, text="Object Names").grid(row=7,column=2*i)
	Label(top, text="Pick Height").grid(row=8,column=2*i)
	Label(top, text="Place Height").grid(row=9,column=2*i)
	Label(top, text="Tag Position").grid(row=10,column=2*i)
	Label(top, text="Gripper Orientation").grid(row=11,column=2*i)
	Label(top, text="Service URL").grid(row=12,column=2*i)
	Label(top, text="Tool URL").grid(row=13,column=2*i)

	robot_name[robot_namelist[i]] = Entry(top)
	robot_command[robot_namelist[i]] = Entry(top)
	height[robot_namelist[i]] = Entry(top)
	home[robot_namelist[i]] = Entry(top)
	calibration_speed[robot_namelist[i]] = Entry(top)
	calibration_start[robot_namelist[i]] = Entry(top)
	calibration_R[robot_namelist[i]] = Entry(top)
	obj_namelists[robot_namelist[i]] = Entry(top)
	pick_height[robot_namelist[i]] = Entry(top)
	place_height[robot_namelist[i]] = Entry(top)
	tag_position[robot_namelist[i]] = Entry(top)
	gripper_orientation[robot_namelist[i]] = Entry(top)
	url[robot_namelist[i]] = Entry(top)
	tool_url[robot_namelist[i]] = Entry(top)

	robot_name[robot_namelist[i]].grid(row=0, column=2*i+1)
	robot_command[robot_namelist[i]].grid(row=1, column=2*i+1)
	height[robot_namelist[i]].grid(row=2, column=2*i+1)
	home[robot_namelist[i]].grid(row=3, column=2*i+1)
	calibration_speed[robot_namelist[i]].grid(row=4, column=2*i+1)
	calibration_start[robot_namelist[i]].grid(row=5, column=2*i+1)
	calibration_R[robot_namelist[i]].grid(row=6, column=2*i+1)
	obj_namelists[robot_namelist[i]].grid(row=7, column=2*i+1)
	pick_height[robot_namelist[i]].grid(row=8, column=2*i+1)
	place_height[robot_namelist[i]].grid(row=9, column=2*i+1)
	tag_position[robot_namelist[i]].grid(row=10, column=2*i+1)
	gripper_orientation[robot_namelist[i]].grid(row=11, column=2*i+1)
	url[robot_namelist[i]].grid(row=12, column=2*i+1)
	tool_url[robot_namelist[i]].grid(row=13, column=2*i+1)

	robot_name[robot_namelist[i]].insert(0,robot_namelist[i])



robot_command['sawyer'].insert(0,'position_command')
height['sawyer'].insert(0,0.93)
home['sawyer'].insert(0,'0.0,0.3,0.3')
calibration_speed['sawyer'].insert(0,'0.05')
calibration_start['sawyer'].insert(0,'0.6,-0.2,0.13')
calibration_R['sawyer'].insert(0,'1.,0.,0.,0.,1.,0.,0.,0.,1.')
obj_namelists['sawyer'].insert(0,'bottle,soap')
pick_height['sawyer'].insert(0,0.105)
place_height['sawyer'].insert(0,0.095)
tag_position['sawyer'].insert(0,-0.045)
gripper_orientation['sawyer'].insert(0,0)
url['sawyer'].insert(0,'rr+tcp://localhost:58654?service=robot')
tool_url['sawyer'].insert(0,'None')

robot_command['ur'].insert(0,'position_command')
height['ur'].insert(0,1.0)
home['ur'].insert(0,'0.3,0.15,0.1')
calibration_speed['ur'].insert(0,'0.07')
calibration_start['ur'].insert(0,'-0.4,0.08,-0.12')
calibration_R['ur'].insert(0,'1.,0.,0.,0.,1.,0.,0.,0.,1.')
obj_namelists['ur'].insert(0,'toothpaste,perfume')
pick_height['ur'].insert(0,0.012)
place_height['ur'].insert(0,0.015)
tag_position['ur'].insert(0,-0.075)
gripper_orientation['ur'].insert(0,0)
url['ur'].insert(0,'rr+tcp://localhost:58653?service=robot')
tool_url['ur'].insert(0,'None')


robot_command['abb'].insert(0,'position_command')
height['abb'].insert(0,0.85)
home['abb'].insert(0,'0.3,0.0,0.3')
calibration_speed['abb'].insert(0,'0.04')
calibration_start['abb'].insert(0,'-0.15,-0.5,0.12')
calibration_R['abb'].insert(0,'0.,1.,0.,-1,0.,0.,0.,0.,1.')
obj_namelists['abb'].insert(0,'perfume,toothpaste')
pick_height['abb'].insert(0,0.142)
place_height['abb'].insert(0,0.14)
tag_position['abb'].insert(0,0.01)
gripper_orientation['abb'].insert(0,float(np.pi/4))
url['abb'].insert(0,'rr+tcp://localhost:58655?service=robot')
tool_url['abb'].insert(0,'None')


#Button
create['sawyer']=Button(top,text='Create sawyer yaml',command=lambda: create_robot_yaml('sawyer'))
calibrate['sawyer']=Button(top,text='Calibrate sawyer',command=lambda: calibrate_robot('sawyer'))
plug['sawyer']=Button(top,text='Plug sawyer',command=lambda: plug_robot('sawyer'),bg='red')
gripper['sawyer']=Button(top,text='gripper off',command=lambda: gripper_ctrl('sawyer'),bg='red')
move_away['sawyer']=Button(top,text='move away',command=lambda: moveaway('sawyer'))
start_job['sawyer']=Button(top,text='start job',command=lambda: startjob('sawyer'))

create['ur']=Button(top,text='Create ur yaml',command=lambda: create_robot_yaml('ur'))
calibrate['ur']=Button(top,text='Calibrate ur',command=lambda: calibrate_robot('ur'))
plug['ur']=Button(top,text='Plug ur',command=lambda: plug_robot('ur'),bg='red')
gripper['ur']=Button(top,text='gripper off',command=lambda: gripper_ctrl('ur'),bg='red')
move_away['ur']=Button(top,text='move away',command=lambda: moveaway('ur'))
start_job['ur']=Button(top,text='start job',command=lambda: startjob('ur'))

create['abb']=Button(top,text='Create abb yaml',command=lambda: create_robot_yaml('abb'))
calibrate['abb']=Button(top,text='Calibrate abb',command=lambda: calibrate_robot('abb'))
plug['abb']=Button(top,text='Plug abb',command=lambda: plug_robot('abb'),bg='red')
gripper['abb']=Button(top,text='gripper off',command=lambda: gripper_ctrl('abb'),bg='red')
move_away['abb']=Button(top,text='move away',command=lambda: moveaway('abb'))
start_job['abb']=Button(top,text='start job',command=lambda: startjob('abb'))

discover['sawyer']=Button(top,text='Discover sawyer',command=lambda: discover_service('sawyer'))
discover['ur']=Button(top,text='Discover ur',command=lambda: discover_service('ur'))
discover['abb']=Button(top,text='Discover abb',command=lambda: discover_service('abb'))



create['sawyer'].grid(row=14,column=0)
calibrate['sawyer'].grid(row=15,column=0)
move_away['sawyer'].grid(row=15,column=1)
plug['sawyer'].grid(row=16,column=0)
gripper['sawyer'].grid(row=16,column=1)
discover['sawyer'].grid(row=14,column=1)
start_job['sawyer'].grid(row=17,column=1)

create['ur'].grid(row=14,column=2)
calibrate['ur'].grid(row=15,column=2)
move_away['ur'].grid(row=15,column=3)
plug['ur'].grid(row=16,column=2)
gripper['ur'].grid(row=16,column=3)
discover['ur'].grid(row=14,column=3)
start_job['ur'].grid(row=17,column=3)

create['abb'].grid(row=14,column=4)
calibrate['abb'].grid(row=15,column=4)
move_away['abb'].grid(row=15,column=5)
plug['abb'].grid(row=16,column=4)
gripper['abb'].grid(row=16,column=5)
discover['abb'].grid(row=14,column=5)
start_job['abb'].grid(row=17,column=5)


 


cognex_sub=RRN.SubscribeService('rr+tcp://localhost:52222/?service=cognex')
cognex_sub.ClientConnectFailed+= connect_failed
cognex_status=Canvas(top, width=20, height=20,bg = 'red')
Label(top, text="Cognex Status: ").grid(row=0,column=6)
cognex_status.grid(row=0,column=7)
detection_wire=cognex_sub.SubscribeWire("detection_wire")
cognex_status.after(500,update_cognex)

try:
	tool_client['sawyer']=RRN.ConnectService(str(tool_url['sawyer'].get()))
except:
	print('sawyer gripper not on')
	pass
try:
	tool_client['ur']=RRN.ConnectService(str(tool_url['ur'].get()))
except:
	print('ur gripper not on')
	pass
try:
	tool_client['abb']=RRN.ConnectService(str(tool_url['abb'].get()))
except:
	print('abb gripper not on')
	pass


robot_sub['sawyer']=RRN.SubscribeService(str(url['sawyer'].get()))
robot_sub['sawyer'].ClientConnectFailed+= connect_failed

state_w['sawyer'] = robot_sub['sawyer'].SubscribeWire("robot_state")
label['sawyer'] = Label(top, fg = "black", justify=LEFT)
label['sawyer'].grid(row=17,column=0)
label['sawyer'].config(text="test")
label['sawyer'].after(500,lambda: update_label('sawyer'))

robot_sub['ur']=RRN.SubscribeService(str(url['ur'].get()))
robot_sub['ur'].ClientConnectFailed+= connect_failed

state_w['ur'] = robot_sub['ur'].SubscribeWire("robot_state")
label['ur'] = Label(top, fg = "black", justify=LEFT)
label['ur'].grid(row=17,column=2)
label['ur'].config(text="test")
label['ur'].after(500,lambda: update_label('ur'))

robot_sub['abb']=RRN.SubscribeService(str(url['abb'].get()))
robot_sub['abb'].ClientConnectFailed+= connect_failed
state_w['abb'] = robot_sub['abb'].SubscribeWire("robot_state")
label['abb'] = Label(top, fg = "black", justify=LEFT)
label['abb'].grid(row=17,column=4)
label['abb'].config(text="test")
label['abb'].after(500,lambda: update_label('abb'))	





top.mainloop()
