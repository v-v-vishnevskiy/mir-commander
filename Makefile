CODE=mir_commander plugins tests
PYTHON?=python3.13
VIRTUAL_ENV?=.venv
COLOUR_GREEN=\033[0;32m
COLOUR_RED=\033[0;31m
END_COLOUR=\033[0m

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
	@./ts_to_qm.sh && ./qrc_to_rcc.sh
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
	@$(VIRTUAL_ENV)/bin/python build_scripts/build.py --only-pyx=true
	@echo "$(COLOUR_GREEN)Building completed successfully!$(END_COLOUR)"

.PHONY: build-lib
build-lib: check-venv  ## Build all python files
	@$(VIRTUAL_ENV)/bin/python build_scripts/build.py
	@echo "$(COLOUR_GREEN)Building completed successfully!$(END_COLOUR)"

.PHONY: build-macos
build-macos: resources build-lib  ## Build .app and .dmg files for macOS
	@$(VIRTUAL_ENV)/bin/cxfreeze bdist_mac
	@find build/Mir\ Commander.app/Contents/Resources/lib/mir_commander -name '*.cpp' -type f -delete
	@find build/Mir\ Commander.app/Contents/Resources/plugins -name '*.cpp' -type f -delete
	@tiffutil -cathidpicheck resources/building/macos/background.png resources/building/macos/background-2x.png -out build/background.tiff
	$(VIRTUAL_ENV)/bin/python build_scripts/build_dmg.py
	@echo "$(COLOUR_GREEN)Building completed successfully!$(END_COLOUR)"

.PHONY: build-linux
build-linux: resources build-lib  ## Build .AppImage file for Linux
	@$(VIRTUAL_ENV)/bin/cxfreeze build_exe
	$(VIRTUAL_ENV)/bin/python build_scripts/build_appimage.py
	@echo "$(COLOUR_GREEN)Building completed successfully!$(END_COLOUR)"

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
