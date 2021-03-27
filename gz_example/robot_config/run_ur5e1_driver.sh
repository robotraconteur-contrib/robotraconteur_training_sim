#!/bin/sh

# RR URL: rr+tcp://localhost:52511?service=robot

dotnet GazeboModelRobotRaconteurDriver.dll --gazebo-url=rr+tcp://localhost:11346/?service=GazeboServer --robotraconteur-tcp-port=52511 --robotraconteur-nodename=ur5e1_robot --model-name=ur5e1 --robot-info-file=ur5e1_robot_default_config.yml

