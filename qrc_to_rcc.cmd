@echo off
call .venv\Scripts\activate
pyside6-rcc --binary resources\icons\general.qrc -o resources\icons\general.rcc
pyside6-rcc --binary resources\icons\items.qrc -o resources\icons\items.rcc
call .venv\Scripts\deactivate
