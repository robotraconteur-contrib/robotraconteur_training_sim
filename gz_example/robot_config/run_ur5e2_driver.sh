#!/bin/sh

# RR URL: rr+tcp://localhost:52512?service=robot

dotnet GazeboModelRobotRaconteurDriver.dll --gazebo-url=rr+tcp://localhost:11346/?service=GazeboServer --robotraconteur-tcp-port=52512 --robotraconteur-nodename=ur5e2_robot --model-name=ur5e2 --robot-info-file=ur5e2_robot_default_config.yml

