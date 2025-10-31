#!/usr/bin/env bash

source .venv/bin/activate

pyside6-rcc --binary resources/icons/general.qrc -o resources/icons/general.rcc
pyside6-rcc --binary resources/icons/project_nodes.qrc -o resources/icons/project_nodes.rcc
