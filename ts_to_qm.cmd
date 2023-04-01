@echo off
call .venv\Scripts\activate
pyside6-lrelease resources\translations\app_ru.ts -qm resources\translations\app_ru.qm
call .venv\Scripts\deactivate
