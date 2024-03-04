@echo off

setlocal

cd /d %~dp0

python -m drekar_launch --config-j2=drekar-launch.yaml.j2 --gui
