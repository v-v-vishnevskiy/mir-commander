#!/usr/bin/env bash

source .venv/bin/activate

pyside6-rcc --binary resources/resources.qrc -o resources/resources.rcc
pyside6-rcc --binary plugins/builtin/resources/resources.qrc -o plugins/builtin/resources/resources.rcc
