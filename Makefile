CODE=mir_commander
PYTHON?=python3.13
VIRTUAL_ENV?=.venv

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv:
	@if [ -d "$(VIRTUAL_ENV)" ]; then \
		echo "Virtual environment already exists at $(VIRTUAL_ENV)"; \
	else \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VIRTUAL_ENV); \
		$(VIRTUAL_ENV)/bin/python -m pip install uv; \
		echo "Virtual environment created at $(VIRTUAL_ENV)"; \
	fi

.PHONY: check-venv
check-venv:
	@if [ ! -d "$(VIRTUAL_ENV)" ]; then \
		echo "Virtual environment not found at $(VIRTUAL_ENV)"; \
		echo "Please run 'make venv' to create a virtual environment."; \
		exit 1; \
	fi

.PHONY: install
install: check-venv
	@VIRTUAL_ENV=$(VIRTUAL_ENV) $(VIRTUAL_ENV)/bin/uv sync --active --all-groups

.PHONY: scripts
scripts: check-venv
	@ln -s $(VIRTUAL_ENV)/bin/mircmd ./mircmd

.PHONY: lint
lint: ## Run linters
	@echo Ruff...
	@$(VIRTUAL_ENV)/bin/ruff check --force-exclude
	@echo Mypy...
	@$(VIRTUAL_ENV)/bin/mypy $(CODE)

.PHONY: format
format: ## Run formatters
	@$(VIRTUAL_ENV)/bin/ruff format --force-exclude

.PHONY: test
test: ## Run tests
	@$(VIRTUAL_ENV)/bin/pytest --cov-report term-missing --cov=mir_commander tests/

.PHONY: pre-commit-install
pre-commit-install:
	@$(VIRTUAL_ENV)/bin/pre-commit install

.PHONY: pre-commit-uninstall
pre-commit-uninstall:
	@$(VIRTUAL_ENV)/bin/pre-commit uninstall

.PHONY: init
init: venv install scripts  ## Initialize the project
	@echo "Project initialized. Activate the virtual environment with 'source $(VIRTUAL_ENV)/bin/activate'"

.PHONY: clean
clean: ## Clean up the project
	@rm -rf __pycache__ .mypy_cache .pytest_cache .ruff_cache .coverage .coverage.*
	@rm -rf mircmd
	@rm -rf $(VIRTUAL_ENV)
	@echo "Cleaned up"
