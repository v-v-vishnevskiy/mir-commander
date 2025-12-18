CODE=mir_commander plugins tests
PYTHON?=python3.13
VIRTUAL_ENV?=.venv
COLOUR_GREEN=\033[0;32m
COLOUR_RED=\033[0;31m
END_COLOUR=\033[0m
ARCH=$(shell uname -m)
SYSTEM=$(shell uname -s | tr '[:upper:]' '[:lower:'])
PYTHON_VERSION=$(shell $(VIRTUAL_ENV)/bin/python --version 2>&1 | awk '{print $$2}' | rev | cut -d"." -f2- | rev)
DOCKER_IMAGE_NAME=mir-commander-linux-builder
APPIMAGETOOL=$(HOME)/.local/bin/appimagetool.AppImage
RUNTIME=$(HOME)/.cache/appimage/runtime
APP_VERSION=$(shell $(VIRTUAL_ENV)/bin/python mir_commander/__init__.py)
APP_NAME=Mir\ Commander
APP_EXEC=mircmd
APP_FILE=MirCommander-$(APP_VERSION)-$(ARCH)


.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv:  ## Create a virtual environment
	@if [ -d "$(VIRTUAL_ENV)" ]; then \
		echo "Virtual environment already exists at $(VIRTUAL_ENV)"; \
	else \
		$(PYTHON) -m venv $(VIRTUAL_ENV); \
		$(VIRTUAL_ENV)/bin/python -m pip install uv; \
		echo "$(COLOUR_GREEN)Virtual environment created at $(VIRTUAL_ENV)$(END_COLOUR)"; \
	fi

.PHONY: check-venv
check-venv:  ## Check if the virtual environment exists
	@if [ ! -d "$(VIRTUAL_ENV)" ]; then \
		echo "$(COLOUR_RED)Virtual environment not found at $(VIRTUAL_ENV)$(END_COLOUR)"; \
		echo "$(COLOUR_RED)Please run 'make venv' to create a virtual environment.$(END_COLOUR)"; \
		exit 1; \
	fi

.PHONY: install
install: check-venv  ## Install all dependencies
	@VIRTUAL_ENV=$(VIRTUAL_ENV) $(VIRTUAL_ENV)/bin/uv sync --active --all-groups
	@echo "$(COLOUR_GREEN)Dependencies installed successfully!$(END_COLOUR)"

mircmd: check-venv  ## Create a symlink to the mircmd script
	@if [ ! -f "mircmd" ]; then \
		ln -s $(VIRTUAL_ENV)/bin/mircmd ./mircmd; \
		echo "$(COLOUR_GREEN)Symlink created successfully!$(END_COLOUR)"; \
	fi

resources: check-venv  ## Generate resources
	@$(VIRTUAL_ENV)/bin/pyside6-lrelease resources/i18n/ru.ts -qm resources/i18n/ru.qm
	@$(VIRTUAL_ENV)/bin/pyside6-lrelease resources/i18n/en.ts -qm resources/i18n/en.qm
	@$(VIRTUAL_ENV)/bin/pyside6-lrelease plugins/builtin/resources/i18n/en.ts -qm plugins/builtin/resources/i18n/en.qm
	@$(VIRTUAL_ENV)/bin/pyside6-lrelease plugins/builtin/resources/i18n/ru.ts -qm plugins/builtin/resources/i18n/ru.qm
	@$(VIRTUAL_ENV)/bin/pyside6-rcc --binary resources/resources.qrc -o resources/resources.rcc
	@$(VIRTUAL_ENV)/bin/pyside6-rcc --binary plugins/builtin/resources/resources.qrc -o plugins/builtin/resources/resources.rcc
	@echo "$(COLOUR_GREEN)Resources generated successfully!$(END_COLOUR)"

.PHONY: scripts
scripts: mircmd

.PHONY: lint
lint: check-venv  ## Run linters
	@$(VIRTUAL_ENV)/bin/ruff check --force-exclude
	@$(VIRTUAL_ENV)/bin/mypy $(CODE)
	@echo "$(COLOUR_GREEN)Linters completed successfully!$(END_COLOUR)"

.PHONY: format
format: check-venv  ## Run formatters
	@$(VIRTUAL_ENV)/bin/ruff format --force-exclude
	@echo "$(COLOUR_GREEN)Formatters completed successfully!$(END_COLOUR)"

.PHONY: test
test: check-venv  ## Run tests
	@$(VIRTUAL_ENV)/bin/pytest --cov-report term-missing --cov=mir_commander tests/
	@echo "$(COLOUR_GREEN)Tests completed successfully!$(END_COLOUR)"

.PHONY: pre-commit-install
pre-commit-install: check-venv  ## Install pre-commit hooks
	@$(VIRTUAL_ENV)/bin/pre-commit install

.PHONY: pre-commit-uninstall
pre-commit-uninstall: check-venv  ## Uninstall pre-commit hooks
	@$(VIRTUAL_ENV)/bin/pre-commit uninstall

.PHONY: init
init: venv install scripts resources  ## Initialize the project
	@echo "$(COLOUR_GREEN)Project initialized. Activate the virtual environment with 'source $(VIRTUAL_ENV)/bin/activate'$(END_COLOUR)"

.PHONY: build-lib-pyx
build-lib-pyx: check-venv  ## Build only .pyx files
	@$(VIRTUAL_ENV)/bin/python build_scripts/build_lib.py --only-pyx
	@echo "$(COLOUR_GREEN)Building completed successfully!$(END_COLOUR)"

.PHONY: build-lib
build-lib: check-venv  ## Build all python files
	@$(VIRTUAL_ENV)/bin/python build_scripts/build_lib.py
	@echo "$(COLOUR_GREEN)Building completed successfully!$(END_COLOUR)"

.PHONY: build-mac
build-mac: resources build-lib  ## Build .app and .dmg files for macOS
	@$(VIRTUAL_ENV)/bin/cxfreeze bdist_mac
	@find build/$(APP_NAME).app/Contents/Resources/lib/mir_commander -name '*.cpp' -type f -delete
	@tiffutil -cathidpicheck resources/building/macos/background.png resources/building/macos/background-2x.png \
	-out build/background.tiff
	$(VIRTUAL_ENV)/bin/python build_scripts/build_dmg.py
	@echo "$(COLOUR_GREEN)Building completed successfully!$(END_COLOUR)"

.PHONY: download-appimagetool
download-appimagetool:  ## Download appimagetool and runtime
	@mkdir -p ~/.local/bin/
	@mkdir -p ~/.cache/appimage/
	@if [ ! -f "$(APPIMAGETOOL)" ]; then \
		wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-$(ARCH).AppImage \
		-O $(APPIMAGETOOL); \
		chmod +x $(APPIMAGETOOL); \
		echo "$(COLOUR_GREEN)Appimagetool downloaded successfully!$(END_COLOUR)"; \
	fi
	@if [ ! -f "$(RUNTIME)" ]; then \
		wget https://github.com/AppImage/type2-runtime/releases/download/continuous/runtime-$(ARCH) \
		-O $(RUNTIME); \
		chmod +x $(RUNTIME); \
		echo "$(COLOUR_GREEN)Runtime downloaded successfully!$(END_COLOUR)"; \
	fi

.PHONY: build-linux
build-linux: resources build-lib download-appimagetool  ## Build .AppImage file for Linux
	@rm -rf build/exe.linux-$(ARCH)-$(PYTHON_VERSION)
	@rm -rf build/AppDir
	@$(VIRTUAL_ENV)/bin/cxfreeze build_exe
	@find build/exe.linux-$(ARCH)-$(PYTHON_VERSION)/lib/mir_commander -name '*.cpp' -type f -delete
	@find build/exe.linux-$(ARCH)-$(PYTHON_VERSION)/lib/mir_commander -name '.DS_Store' -type f -delete
	@mkdir -p build/AppDir
	@cp -r build/exe.linux-$(ARCH)-$(PYTHON_VERSION)/* build/AppDir
	@echo "[Desktop Entry]\n\
Type=Application\n\
Version=1.5\n\
Name=$(shell echo $(APP_NAME))\n\
Exec=$(APP_EXEC) %F\n\
Comment=A modern, powerful graphical user interface for molecular structure modeling.\n\
Icon=$(APP_EXEC)\n\
Categories=Science;\n\
Terminal=false" > build/AppDir/$(APP_EXEC).desktop
	@echo '#!/bin/sh\nexec "$$APPDIR/$(APP_EXEC)" "$$@"' > build/AppDir/AppRun
	@chmod +x build/AppDir/AppRun
	@cp build/AppDir/icon.png build/AppDir/.DirIcon
	@mv build/AppDir/icon.png build/AppDir/$(APP_EXEC).png
	$(APPIMAGETOOL) \
	--appimage-extract-and-run \
	--runtime-file $(RUNTIME) \
	--no-appstream \
	build/AppDir \
	build/$(APP_FILE).AppImage
	@echo "$(COLOUR_GREEN)Building completed successfully!$(END_COLOUR)"

.PHONY: build-linux-docker-%
build-linux-docker-%:
	@rm -rf build/linux-$*
	@mkdir -p build/linux-$*
	@echo "$(COLOUR_GREEN)Building Docker image for $*...$(END_COLOUR)"
	@docker buildx build --platform linux/$* --file Dockerfile.linux --tag $(DOCKER_IMAGE_NAME):$* --target builder --build-arg FIX_APPAIMGETOOL=$(shell [ "$(ARCH)" != "$*" ] && echo "true" || echo "false") --load .
	@echo "$(COLOUR_GREEN)Building AppImage for $*...$(END_COLOUR)"
	@docker run --platform linux/$* --rm -v $(PWD)/build/linux-$*:/build/build $(DOCKER_IMAGE_NAME):$*
	@echo "$(COLOUR_GREEN)AppImage build ($*) completed successfully!$(END_COLOUR)"

.PHONY: build-linux-docker
build-linux-docker: build-linux-docker-amd64 build-linux-docker-arm64  ## Build .AppImage file for Linux using Docker (all architectures)
	@echo "$(COLOUR_GREEN)Docker build completed successfully!$(END_COLOUR)"

.PHONY: clean-cpp
clean-cpp:  ## Clean C++ build artifacts
	@find mir_commander -name '*.cpp' -type f -delete
	@find mir_commander -name '*.c' -type f -delete
	@find plugins -name '*.cpp' -type f -delete
	@find plugins -name '*.c' -type f -delete
	@echo "$(COLOUR_GREEN)C++ build artifacts cleaned successfully!$(END_COLOUR)"

.PHONY: clean-build
clean-build: clean-cpp  ## Clean build artifacts
	@find mir_commander -name '*.so' -type f -delete
	@find plugins -name '*.so' -type f -delete
	@rm -rf build
	@rm -rf dist
	@echo "$(COLOUR_GREEN)Build artifacts cleaned successfully!$(END_COLOUR)"

.PHONY: clean
clean: clean-build  ## Clean up the project
	@rm -rf __pycache__ .mypy_cache .pytest_cache .ruff_cache .coverage .coverage.*
	@rm -rf mircmd
	@find plugins -name '*.rcc' -type f -delete
	@rm -rf $(VIRTUAL_ENV)
	@echo "$(COLOUR_GREEN)Cleaning up completed successfully!$(END_COLOUR)"
