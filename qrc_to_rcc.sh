#!/usr/bin/env bash

source .venv/bin/activate

pyside6-rcc --binary resources/icons.qrc -o resources/icons.rcc

pyside6-rcc --binary plugins/builtin/resources/icons.qrc -o plugins/builtin/resources/icons.rcc
