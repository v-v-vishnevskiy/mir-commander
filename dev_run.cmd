@echo off
call .venv/Scripts/activate
set PYTHONPATH=%~dp0
.venv\Scripts\mircmd.exe %*
call .venv/Scripts/deactivate
