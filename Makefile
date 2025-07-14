# FLEXT Tap LDIF - Standardized Project Makefile
# This file follows the standardized template for FLEXT projects

.PHONY: help install dev-install test lint type-check format check clean build docs setup
.DEFAULT_GOAL := help

# Project Configuration
PROJECT_NAME := flext-tap-ldif
PACKAGE_NAME := flext_tap_ldif
PYTHON_VERSION := 3.13

# Path Configuration
SRC_DIR := src
TEST_DIR := tests
REPORTS_DIR := reports

# Virtual Environment Detection
VENV_PATH := $(shell poetry env info --path 2>/dev/null)
ifeq ($(VENV_PATH),)
    PYTHON := python
    PIP := pip
else
    PYTHON := $(VENV_PATH)/bin/python
    PIP := $(VENV_PATH)/bin/pip
endif

# Colors for output
RESET := \033[0m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
BLUE := \033[34m

help: ## Show this help message
	@echo "$(GREEN)FLEXT Tap LDIF - Available Commands$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(BLUE)%-15s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# =============================================================================
# Development Environment Setup
# =============================================================================

install: ## Install production dependencies
	@echo "$(GREEN)Installing production dependencies...$(RESET)"
	poetry install --only=main

dev-install: install ## Install all dependencies including dev dependencies
	@echo "$(GREEN)Installing development dependencies...$(RESET)"
	poetry install
	@echo "$(GREEN)Installing pre-commit hooks...$(RESET)"
	poetry run pre-commit install

setup: dev-install ## Complete development environment setup
	@echo "$(GREEN)Development environment ready!$(RESET)"

# =============================================================================
# Code Quality & Testing
# =============================================================================

test: ## Run tests with coverage
	@echo "$(GREEN)Running tests...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	poetry run pytest $(TEST_DIR)

test-unit: ## Run unit tests only
	@echo "$(GREEN)Running unit tests...$(RESET)"
	poetry run pytest $(TEST_DIR) -m "unit"

test-integration: ## Run integration tests only
	@echo "$(GREEN)Running integration tests...$(RESET)"
	poetry run pytest $(TEST_DIR) -m "integration"

test-watch: ## Run tests in watch mode
	@echo "$(GREEN)Running tests in watch mode...$(RESET)"
	poetry run pytest-watch $(TEST_DIR)

lint: ## Run code linting
	@echo "$(GREEN)Running linting...$(RESET)"
	poetry run ruff check $(SRC_DIR) $(TEST_DIR)

lint-fix: ## Run code linting with auto-fix
	@echo "$(GREEN)Running linting with auto-fix...$(RESET)"
	poetry run ruff check --fix $(SRC_DIR) $(TEST_DIR)

type-check: ## Run type checking
	@echo "$(GREEN)Running type checking...$(RESET)"
	poetry run mypy $(SRC_DIR) $(TEST_DIR)

format: ## Format code
	@echo "$(GREEN)Formatting code...$(RESET)"
	poetry run ruff format $(SRC_DIR) $(TEST_DIR)

format-check: ## Check code formatting
	@echo "$(GREEN)Checking code formatting...$(RESET)"
	poetry run ruff format --check $(SRC_DIR) $(TEST_DIR)

security: ## Run security checks
	@echo "$(GREEN)Running security checks...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	poetry run bandit -r $(SRC_DIR) -f json -o $(REPORTS_DIR)/security.json || true
	poetry run bandit -r $(SRC_DIR)

check: lint type-check format-check security test ## Run all quality checks
	@echo "$(GREEN)All quality checks completed!$(RESET)"

# =============================================================================
# Singer Tap Specific Commands
# =============================================================================

discover: ## Run Singer discovery
	@echo "$(GREEN)Running Singer discovery...$(RESET)"
	poetry run tap-ldif --discover

catalog: ## Generate Singer catalog
	@echo "$(GREEN)Generating Singer catalog...$(RESET)"
	poetry run tap-ldif --discover > catalog.json

sync: ## Run Singer sync (requires config.json and catalog.json)
	@echo "$(GREEN)Running Singer sync...$(RESET)"
	poetry run tap-ldif --config config.json --catalog catalog.json

validate-config: ## Validate configuration
	@echo "$(GREEN)Validating configuration...$(RESET)"
	@if [ ! -f config.json ]; then echo "$(RED)config.json not found$(RESET)"; exit 1; fi
	poetry run tap-ldif --config config.json --discover > /dev/null

# =============================================================================
# Build & Distribution
# =============================================================================

build: clean ## Build distribution packages
	@echo "$(GREEN)Building distribution packages...$(RESET)"
	poetry build

build-wheel: clean ## Build wheel package only
	@echo "$(GREEN)Building wheel package...$(RESET)"
	poetry build --format wheel

build-sdist: clean ## Build source distribution only
	@echo "$(GREEN)Building source distribution...$(RESET)"
	poetry build --format sdist

# =============================================================================
# Documentation
# =============================================================================

docs: ## Generate documentation
	@echo "$(GREEN)Generating documentation...$(RESET)"
	poetry run mkdocs build

docs-serve: ## Serve documentation locally
	@echo "$(GREEN)Serving documentation at http://127.0.0.1:8000$(RESET)"
	poetry run mkdocs serve

docs-deploy: ## Deploy documentation
	@echo "$(GREEN)Deploying documentation...$(RESET)"
	poetry run mkdocs gh-deploy

# =============================================================================
# Maintenance & Cleanup
# =============================================================================

clean: ## Clean build artifacts and cache
	@echo "$(GREEN)Cleaning build artifacts...$(RESET)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf $(REPORTS_DIR)/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

clean-all: clean ## Clean everything including virtual environment
	@echo "$(GREEN)Cleaning virtual environment...$(RESET)"
	poetry env remove --all || true

update: ## Update dependencies
	@echo "$(GREEN)Updating dependencies...$(RESET)"
	poetry update

update-dev: ## Update development dependencies
	@echo "$(GREEN)Updating development dependencies...$(RESET)"
	poetry update --group dev

# =============================================================================
# Release Management
# =============================================================================

version: ## Show current version
	@poetry version

version-patch: ## Bump patch version
	@echo "$(GREEN)Bumping patch version...$(RESET)"
	poetry version patch

version-minor: ## Bump minor version
	@echo "$(GREEN)Bumping minor version...$(RESET)"
	poetry version minor

version-major: ## Bump major version
	@echo "$(GREEN)Bumping major version...$(RESET)"
	poetry version major

# =============================================================================
# Project Information
# =============================================================================

info: ## Show project information
	@echo "$(BLUE)Project: $(PROJECT_NAME)$(RESET)"
	@echo "$(BLUE)Package: $(PACKAGE_NAME)$(RESET)"
	@echo "$(BLUE)Python: $(PYTHON_VERSION)$(RESET)"
	@echo "$(BLUE)Poetry Version: $$(poetry version -s)$(RESET)"
	@echo "$(BLUE)Virtual Environment: $(VENV_PATH)$(RESET)"

deps: ## Show dependency tree
	@echo "$(GREEN)Dependency tree:$(RESET)"
	poetry show --tree

deps-outdated: ## Show outdated dependencies
	@echo "$(GREEN)Outdated dependencies:$(RESET)"
	poetry show --outdated

# =============================================================================
# Git Integration
# =============================================================================

pre-commit: check ## Run pre-commit checks manually
	@echo "$(GREEN)Running pre-commit checks...$(RESET)"
	poetry run pre-commit run --all-files

commit-check: check ## Check if code is ready for commit
	@echo "$(GREEN)Code is ready for commit!$(RESET)"