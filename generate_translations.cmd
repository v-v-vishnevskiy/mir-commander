@echo off
call .venv\Scripts\activate
pyside6-lupdate mir_commander\main_window.py mir_commander\widgets\about.py -ts resources\translations\app_ru.ts
call .venv\Scripts\deactivate
