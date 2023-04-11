#!/usr/bin/env bash

source .venv/bin/activate

pyside6-lupdate mir_commander/*.py mir_commander/widgets/*.py mir_commander/widgets/settings/*.py mir_commander/widgets/dock_widget/*.py -ts resources/i18n/app_ru.ts
pyside6-lupdate mir_commander/*.py mir_commander/widgets/*.py mir_commander/widgets/settings/*.py mir_commander/widgets/dock_widget/*.py -ts resources/i18n/app_en.ts
