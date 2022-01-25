@echo off
set here=%~dp0
set py_dir=%here%..\src\py\
rem echo %here%
rem echo %py_dir%
python %py_dir%tokenise.py %1 | ^
python %py_dir%parse1_indent.py - | ^
python %py_dir%parse2_syntax.py -

