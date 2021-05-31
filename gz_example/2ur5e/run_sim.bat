@echo off

setlocal

set GAZEBO_MODEL_PATH=%GAZEBO_MODEL_PATH%;%~dp0\..\models

cd %~dp0
if %errorlevel% neq 0 exit /b %errorlevel%
start cmd /c gazebo --verbose tsp_world.world -s gazebo_robotraconteur_server_plugin.dll --robotraconteur-server-tcp-port=11346
if %errorlevel% neq 0 exit /b %errorlevel%

timeout /t 10
cd %~dp0
if %errorlevel% neq 0 exit /b %errorlevel%
python initialization.py
if %errorlevel% neq 0 exit /b %errorlevel%

cd %~dp0\..\robot_config
if %errorlevel% neq 0 exit /b %errorlevel%
start cmd /c gazebo_model_robotraconteur_driver --gazebo-url=rr+tcp://localhost:11346/?service=GazeboServer --robotraconteur-tcp-port=52511 --robotraconteur-nodename=ur5e1_robot --model-name=ur5e1 --robot-info-file=ur5e1_robot_default_config.yml
if %errorlevel% neq 0 exit /b %errorlevel%

start cmd /c gazebo_model_robotraconteur_driver --gazebo-url=rr+tcp://localhost:11346/?service=GazeboServer --robotraconteur-tcp-port=52512 --robotraconteur-nodename=ur5e2_robot --model-name=ur5e2 --robot-info-file=ur5e2_robot_default_config.yml
if %errorlevel% neq 0 exit /b %errorlevel%

cd %~dp0\gripper
start cmd /c python gripper_service.py --robotraconteur-tcp-port=52521 --robotraconteur-nodename=ur5e1_gripper --tool-info-file=gazebo_link_attacher1_tool_info.yml --gazebo-gripper-link=ur5e1::gripper::body --gazebo-gripper-contact-sensor=ur5e1::gripper::body::contact_sensor --gazebo-payload-prefix=round_bottle,perfume,cube
if %errorlevel% neq 0 exit /b %errorlevel%

start cmd /c python gripper_service.py --robotraconteur-tcp-port=52522 --robotraconteur-nodename=ur5e2_gripper --tool-info-file=gazebo_link_attacher2_tool_info.yml --gazebo-gripper-link=ur5e2::gripper::body --gazebo-gripper-contact-sensor=ur5e2::gripper::body::contact_sensor --gazebo-payload-prefix=round_bottle,perfume,cube
if %errorlevel% neq 0 exit /b %errorlevel%

cd %~dp0\camera
start cmd /c python camera_service.py --camera-info-file=camerasensor.yaml
if %errorlevel% neq 0 exit /b %errorlevel%

timeout /t 5
cd %~dp0
if %errorlevel% neq 0 exit /b %errorlevel%
python home.py
if %errorlevel% neq 0 exit /b %errorlevel%
rem python gui_client_robot.py --robot-name=2ur5e1
if %errorlevel% neq 0 exit /b %errorlevel%

