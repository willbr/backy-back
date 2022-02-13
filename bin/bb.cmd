@echo off
set here=%~dp0
set py_dir=%here%..\src\
rem echo %here%
rem echo %py_dir%
python %py_dir%eval.py %*

