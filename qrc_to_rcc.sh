#!/usr/bin/env bash

source .venv/bin/activate

pyside6-rcc --binary resources/icons/general.qrc -o resources/icons/general.rcc
