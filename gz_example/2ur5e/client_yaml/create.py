import yaml

client_ur = {"robot_name":"ur","height":0.87,"obj_namelists":['tp','pf'],"home":[-0.29,0.19,0.3],"tag_position":-0.05,"pick_height":0.03,"place_height":0.03,"calibration_start":[-0.4,0.08,-0.12],"calibration_speed":0.07,"robot_command":"position_command","url":'rr+tcp://[fe80::76d6:e60f:27f6:1e3e]:58652/?nodeid=55ade648-a8c2-4775-a7ec-645acea83525&service=robot'}
client_sawyer = {"robot_name":"sawyer","height":0.78,"obj_namelists":['bt','sp'],"home":[-0.1,0.3,0.3],"tag_position":-0.05,"pick_height":0.105,"place_height":0.095,"calibration_start":[0.55,-0.2,0.13],"calibration_speed":0.05,"robot_command":"velocity_command","url":'rr+tcp://[fe80::a2c:1efa:1c07:f043]:58654/?nodeid=8edf99b5-96b5-4b84-9acf-952af15f0918&service=robot'}
client_abb = {"robot_name":"abb","height":0.79,"obj_namelists":['bt','sp'],"home":[-0.1,0.3,0.4],"tag_position":-0.05,"pick_height":0.1,"place_height":0.1,"calibration_start":[0.55,0.08,0.2],"calibration_speed":0.05,"robot_command":"position_command","url":'rr+tcp://[fe80::16ff:3758:dcde:4e15]:58651/?nodeid=16a22280-7458-4ce9-bd4d-29b55782a2e1&service=robot'}
client_staubli = {"robot_name":"staubli","height":1.0,"obj_namelists":['sp'],"home":[0.3,0.0,0.3],"pick_height":-0.03,"place_height":-0.1,"url":'rr+tcp://bbb4.local:58656?service=abb'}

with open(r'client_ur.yaml', 'w') as file:
    documents = yaml.dump(client_ur, file)
with open(r'client_sawyer.yaml', 'w') as file:
    documents = yaml.dump(client_sawyer, file)
with open(r'client_abb.yaml', 'w') as file:
    documents = yaml.dump(client_abb, file)
with open(r'client_staubli.yaml', 'w') as file:
    documents = yaml.dump(client_staubli, file)


with open(r'client_ur.yaml') as file:
    documents = yaml.load(file, Loader=yaml.FullLoader)
    print(documents)