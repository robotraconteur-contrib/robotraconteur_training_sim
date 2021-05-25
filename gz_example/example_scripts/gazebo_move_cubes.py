from RobotRaconteur.Client import *
from RobotRaconteurCompanion.Util.GeometryUtil import GeometryUtil

server = RRN.ConnectService('rr+tcp://localhost:11346?service=GazeboServer')

geom_util = GeometryUtil(client_obj=server)

world = server.get_worlds('default')

for i in range(4):
    model_name = f"cube200{i}"
    model = world.get_models(model_name)
    p = geom_util.xyz_rpy_to_pose([-0.2,-0.2-i*0.1,1.1],[0.0,0.0,0.0])
    model.setf_world_pose(p)
