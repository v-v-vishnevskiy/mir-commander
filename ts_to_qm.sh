#!/usr/bin/env bash

source .venv/bin/activate

pyside6-lrelease resources/i18n/app_ru.ts -qm resources/i18n/app_ru.qm
pyside6-lrelease resources/i18n/app_en.ts -qm resources/i18n/app_en.qm
