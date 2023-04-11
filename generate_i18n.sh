#!/usr/bin/env bash

source .venv/bin/activate

# Collect all py files in the mir_commander directory,
pyfpaths=$(find mir_commander -type f -name "*.py")
pyfpaths="${pyfpaths//$'\n'/ }" # replace newlines by spaces

# and generate/update ts files.
pyside6-lupdate $pyfpaths -ts resources/i18n/app_en.ts
pyside6-lupdate $pyfpaths -ts resources/i18n/app_ru.ts
