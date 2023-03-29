@echo off
call .venv/Scripts/activate
set PYTHONPATH=%~dp0
python mir_commander
call .venv/Scripts/deactivate
