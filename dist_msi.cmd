@echo off
call .venv\Scripts\activate

call resources.cmd

call .venv\Scripts\activate

call python build_scripts/build_lib.py

powershell.exe -Command "Remove-Item -Path mir_commander -Include *.cpp -Recurse -Force"
powershell.exe -Command "Remove-Item -Path plugins -Include *.cpp -Recurse -Force"

call cxfreeze bdist_msi

call .venv\Scripts\deactivate
