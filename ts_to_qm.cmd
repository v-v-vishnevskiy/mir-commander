@echo off
call .venv\Scripts\activate
pyside6-lrelease resources\i18n\app_ru.ts -qm resources\i18n\app_ru.qm
call .venv\Scripts\deactivate
