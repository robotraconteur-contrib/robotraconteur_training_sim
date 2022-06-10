@echo off

setlocal

set GAZEBO_MODEL_PATH=%GAZEBO_MODEL_PATH%;%~dp0\..\models

cd %~dp0
if %errorlevel% neq 0 exit /b %errorlevel%
rem start cmd /c gazebo --verbose create_world.world -s gazebo_robotraconteur_server_plugin.dll --robotraconteur-server-tcp-port=11346
gazebo --verbose create_world.world -s gazebo_robotraconteur_server_plugin.dll --robotraconteur-server-tcp-port=11346
if %errorlevel% neq 0 exit /b %errorlevel%