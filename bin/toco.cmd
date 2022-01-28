@echo off
set here=%~dp0
set py_dir=%here%..\src\py\
rem echo %here%
rem echo %py_dir%
python %py_dir%toco.py %1

