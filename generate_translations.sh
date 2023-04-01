#!/usr/bin/env bash

source .venv/bin/activate

pyside6-lupdate mir_commander/main_window.py mir_commander/widgets/about.py -ts resources/translations/app_ru.ts
pyside6-lrelease resources/translations/app_ru.ts -qm resources/translations/app_ru.qm
