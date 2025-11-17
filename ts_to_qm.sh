#!/usr/bin/env bash

source .venv/bin/activate

pyside6-lrelease resources/i18n/ru.ts -qm resources/i18n/ru.qm
pyside6-lrelease resources/i18n/en.ts -qm resources/i18n/en.qm

pyside6-lrelease plugins/builtin/resources/i18n/en.ts -qm plugins/builtin/resources/i18n/en.qm
pyside6-lrelease plugins/builtin/resources/i18n/ru.ts -qm plugins/builtin/resources/i18n/ru.qm
