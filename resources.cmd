@echo off
call .venv\Scripts\activate
pyside6-lrelease resources\i18n\en.ts -qm resources\i18n\en.qm
pyside6-lrelease resources\i18n\ru.ts -qm resources\i18n\ru.qm

pyside6-lrelease plugins\builtin\resources\i18n\en.ts -qm plugins\builtin\resources\i18n\en.qm
pyside6-lrelease plugins\builtin\resources\i18n\ru.ts -qm plugins\builtin\resources\i18n\ru.qm

pyside6-rcc --binary resources\resources.qrc -o resources\resources.rcc
pyside6-rcc --binary plugins\builtin\resources\resources.qrc -o plugins\builtin\resources\resources.rcc
call .venv\Scripts\deactivate
