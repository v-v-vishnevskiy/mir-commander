@echo off
call .venv\Scripts\activate
pyside6-rcc --binary resources\icons\general.qrc -o resources\icons\general.rcc
call .venv\Scripts\deactivate
