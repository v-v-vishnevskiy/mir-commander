#!/usr/bin/env bash

source .venv/bin/activate

pyside6-lupdate mir_commander/*.py mir_commander/widgets/*.py -ts resources/i18n/app_ru.ts
