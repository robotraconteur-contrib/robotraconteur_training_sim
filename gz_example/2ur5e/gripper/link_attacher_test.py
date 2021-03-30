from RobotRaconteur.Client import *
from pathlib import Path
import sys
import os
import uuid
import numpy as np
import re
import time

sys.path.append(str(Path(os.path.realpath(__file__)).parent.parent.parent.joinpath("toolbox")))
import general_robotics_toolbox as rox

# Test script using link attacher method to grab and release objects

robot_model_name = "ur5e1"

payload_prefix = ["round_bottle","perfume"]

server = RRN.ConnectService('rr+tcp://localhost:11346?service=GazeboServer')
gripper1_contact_sensor = server.get_sensors(f'default::{robot_model_name}::gripper::body::contact_sensor')
world = server.get_worlds('default')
ur5e1 = world.get_models(robot_model_name)
gripper1 = ur5e1.get_child_models("gripper")
gripper1_body = gripper1.get_links("body")

contacts=gripper1_contact_sensor.contacts.PeekInValue()[0]

contacted_object = None

model_name = None
link_name = None

for c in contacts:
    c_name = c.contact_name1

    for p in payload_prefix:
        re_m = re.match(f"^({p}.*)::(\w+)::\w+$",c_name)
        if re_m:
            model_name=re_m.group(1)
            link_name=re_m.group(2)
            break
    if link_name is not None:
        break
   

assert model_name is not None

gripper1_body.attach_link(model_name,link_name)

time.sleep(5)

gripper1_body.detach_link(model_name, link_name)

