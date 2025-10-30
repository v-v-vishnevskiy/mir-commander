@echo off
call .venv\Scripts\activate
pyside6-rcc --binary resources\icons\general.qrc -o resources\icons\general.rcc
pyside6-rcc --binary resources\icons\project_nodes.qrc -o resources\icons\project_nodes.rcc
call .venv\Scripts\deactivate
