#!/usr/bin/env bash

source .venv/bin/activate

pyside6-lrelease resources/translations/app_ru.ts -qm resources/translations/app_ru.qm
