from RobotRaconteur.Client import *
from RobotRaconteurCompanion.Util.GeometryUtil import GeometryUtil

server = RRN.ConnectService('rr+tcp://localhost:11346?service=GazeboServer')

geom_util = GeometryUtil(client_obj=server)

world = server.get_worlds('default')


model = world.get_models("camera")
p = geom_util.xyz_rpy_to_pose([0.,0.,1.7],[0.0,0.0,0.0])
model.setf_world_pose(p)