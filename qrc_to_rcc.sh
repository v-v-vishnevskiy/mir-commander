#!/usr/bin/env bash

source .venv/bin/activate

pyside6-rcc resources/icons/general.qrc --binary -o resources/icons/general.rcc
