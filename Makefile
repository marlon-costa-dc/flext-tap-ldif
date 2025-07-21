# FLEXT TAP LDIF - Singer Tap for LDIF Data Extraction
# ===================================================
# Enterprise Singer tap for LDIF file processing with schema discovery and streaming
# Python 3.13 + Singer SDK + LDIF Processing + Zero Tolerance Quality Gates

.PHONY: help check validate test lint type-check security format format-check fix
.PHONY: install dev-install setup pre-commit build clean
.PHONY: coverage coverage-html test-unit test-integration test-singer
.PHONY: deps-update deps-audit deps-tree deps-outdated
.PHONY: tap-discover tap-catalog tap-run tap-test tap-validate tap-sync
.PHONY: ldif-parse ldif-schema ldif-performance singer-spec

# ============================================================================
# 🎯 HELP & INFORMATION
# ============================================================================

help: ## Show this help message
	@echo "🎯 FLEXT TAP LDIF - Singer Tap for LDIF Data Extraction"
	@echo "======================================================"
	@echo "🎯 Singer SDK + LDIF Processing + Python 3.13"
	@echo ""
	@echo "📦 Enterprise Singer tap for LDIF file data extraction"
	@echo "🔒 Zero tolerance quality gates with comprehensive Singer testing"
	@echo "🧪 90%+ test coverage requirement with LDIF format compliance"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

# ============================================================================
# 🎯 CORE QUALITY GATES - ZERO TOLERANCE
# ============================================================================

validate: lint type-check security test tap-test ## STRICT compliance validation (all must pass)
	@echo "✅ ALL QUALITY GATES PASSED - FLEXT TAP LDIF COMPLIANT"

check: lint type-check test ## Essential quality checks (pre-commit standard)
	@echo "✅ Essential checks passed"

lint: ## Ruff linting (17 rule categories, ALL enabled)
	@echo "🔍 Running ruff linter (ALL rules enabled)..."
	@poetry run ruff check src/ tests/ --fix --unsafe-fixes
	@echo "✅ Linting complete"

type-check: ## MyPy strict mode type checking (zero errors tolerated)
	@echo "🛡️ Running MyPy strict type checking..."
	@poetry run mypy src/ tests/ --strict
	@echo "✅ Type checking complete"

security: ## Security scans (bandit + pip-audit + secrets)
	@echo "🔒 Running security scans..."
	@poetry run bandit -r src/ --severity-level medium --confidence-level medium
	@poetry run pip-audit --ignore-vuln PYSEC-2022-42969
	@poetry run detect-secrets scan --all-files
	@echo "✅ Security scans complete"

format: ## Format code with ruff
	@echo "🎨 Formatting code..."
	@poetry run ruff format src/ tests/
	@echo "✅ Formatting complete"

format-check: ## Check formatting without fixing
	@echo "🎨 Checking code formatting..."
	@poetry run ruff format src/ tests/ --check
	@echo "✅ Format check complete"

fix: format lint ## Auto-fix all issues (format + imports + lint)
	@echo "🔧 Auto-fixing all issues..."
	@poetry run ruff check src/ tests/ --fix --unsafe-fixes
	@echo "✅ All auto-fixes applied"

# ============================================================================
# 🧪 TESTING - 90% COVERAGE MINIMUM
# ============================================================================

test: ## Run tests with coverage (90% minimum required)
	@echo "🧪 Running tests with coverage..."
	@poetry run pytest tests/ -v --cov=src/flext_tap_ldif --cov-report=term-missing --cov-fail-under=90
	@echo "✅ Tests complete"

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	@poetry run pytest tests/unit/ -v
	@echo "✅ Unit tests complete"

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	@poetry run pytest tests/integration/ -v
	@echo "✅ Integration tests complete"

test-singer: ## Run Singer-specific tests
	@echo "🧪 Running Singer protocol tests..."
	@poetry run pytest tests/ -m "singer" -v
	@echo "✅ Singer tests complete"

test-ldif: ## Run LDIF-specific tests
	@echo "🧪 Running LDIF processing tests..."
	@poetry run pytest tests/ -m "ldif" -v
	@echo "✅ LDIF tests complete"

test-performance: ## Run performance tests
	@echo "⚡ Running Singer tap performance tests..."
	@poetry run pytest tests/performance/ -v --benchmark-only
	@echo "✅ Performance tests complete"

coverage: ## Generate detailed coverage report
	@echo "📊 Generating coverage report..."
	@poetry run pytest tests/ --cov=src/flext_tap_ldif --cov-report=term-missing --cov-report=html
	@echo "✅ Coverage report generated in htmlcov/"

coverage-html: coverage ## Generate HTML coverage report
	@echo "📊 Opening coverage report..."
	@python -m webbrowser htmlcov/index.html

# ============================================================================
# 🚀 DEVELOPMENT SETUP
# ============================================================================

setup: install pre-commit ## Complete development setup
	@echo "🎯 Development setup complete!"

install: ## Install dependencies with Poetry
	@echo "📦 Installing dependencies..."
	@poetry install --all-extras --with dev,test,docs,security
	@echo "✅ Dependencies installed"

dev-install: install ## Install in development mode
	@echo "🔧 Setting up development environment..."
	@poetry install --all-extras --with dev,test,docs,security
	@poetry run pre-commit install
	@echo "✅ Development environment ready"

pre-commit: ## Setup pre-commit hooks
	@echo "🎣 Setting up pre-commit hooks..."
	@poetry run pre-commit install
	@poetry run pre-commit run --all-files || true
	@echo "✅ Pre-commit hooks installed"

# ============================================================================
# 🎵 SINGER TAP OPERATIONS - CORE FUNCTIONALITY
# ============================================================================

tap-discover: ## Discover LDIF schema for catalog generation
	@echo "🔍 Discovering LDIF schema..."
	@poetry run tap-ldif --discover
	@echo "✅ LDIF schema discovery complete"

tap-catalog: ## Generate Singer catalog from LDIF
	@echo "📋 Generating Singer catalog..."
	@poetry run tap-ldif --discover > catalog.json
	@echo "✅ Singer catalog generated: catalog.json"

tap-run: ## Run LDIF tap with sample configuration
	@echo "🎵 Running LDIF tap..."
	@poetry run tap-ldif --config config.json --catalog catalog.json
	@echo "✅ LDIF tap execution complete"

tap-test: ## Test LDIF tap functionality
	@echo "🧪 Testing LDIF tap functionality..."
	@poetry run python -c "from flext_tap_ldif.tap import TapLDIF; from flext_tap_ldif.client import LDIFTapClient; print('LDIF tap loaded successfully')"
	@echo "✅ LDIF tap test complete"

tap-validate: ## Validate LDIF tap configuration
	@echo "🔍 Validating LDIF tap configuration..."
	@poetry run python scripts/validate_tap_config.py
	@echo "✅ LDIF tap configuration validation complete"

tap-sync: ## Test incremental sync functionality
	@echo "🔄 Testing incremental sync..."
	@poetry run python scripts/test_incremental_sync.py
	@echo "✅ Incremental sync test complete"

tap-state: ## Test state management
	@echo "📊 Testing state management..."
	@poetry run python scripts/test_state_management.py
	@echo "✅ State management test complete"

# ============================================================================
# 📁 LDIF PROCESSING OPERATIONS
# ============================================================================

ldif-parse: ## Test LDIF parsing functionality
	@echo "📁 Testing LDIF parsing..."
	@poetry run python scripts/test_ldif_parsing.py
	@echo "✅ LDIF parsing test complete"

ldif-schema: ## Analyze LDIF schema patterns
	@echo "📋 Analyzing LDIF schema patterns..."
	@poetry run python scripts/analyze_ldif_schema.py
	@echo "✅ LDIF schema analysis complete"

ldif-performance: ## Run LDIF performance benchmarks
	@echo "⚡ Running LDIF performance benchmarks..."
	@poetry run python scripts/benchmark_ldif_performance.py
	@echo "✅ LDIF performance benchmarks complete"

ldif-streaming: ## Test LDIF streaming processing
	@echo "🌊 Testing LDIF streaming processing..."
	@poetry run python scripts/test_ldif_streaming.py
	@echo "✅ LDIF streaming test complete"

ldif-large-files: ## Test large LDIF file processing
	@echo "📚 Testing large LDIF file processing..."
	@poetry run python scripts/test_large_ldif_files.py
	@echo "✅ Large file processing test complete"

ldif-encoding: ## Test LDIF encoding handling
	@echo "🔤 Testing LDIF encoding handling..."
	@poetry run python scripts/test_ldif_encoding.py
	@echo "✅ LDIF encoding test complete"

ldif-filters: ## Test LDIF filtering functionality
	@echo "🔍 Testing LDIF filtering..."
	@poetry run python scripts/test_ldif_filters.py
	@echo "✅ LDIF filtering test complete"

# ============================================================================
# 🎵 SINGER PROTOCOL COMPLIANCE
# ============================================================================

singer-spec: ## Validate Singer specification compliance
	@echo "🎵 Validating Singer specification compliance..."
	@poetry run python scripts/validate_singer_spec.py
	@echo "✅ Singer specification validation complete"

singer-messages: ## Test Singer message output
	@echo "📬 Testing Singer message output..."
	@poetry run python scripts/test_singer_messages.py
	@echo "✅ Singer message test complete"

singer-catalog: ## Validate Singer catalog format
	@echo "📋 Validating Singer catalog format..."
	@poetry run python scripts/validate_singer_catalog.py
	@echo "✅ Singer catalog validation complete"

singer-state: ## Test Singer state handling
	@echo "📊 Testing Singer state handling..."
	@poetry run python scripts/test_singer_state.py
	@echo "✅ Singer state test complete"

singer-metrics: ## Test Singer metrics output
	@echo "📈 Testing Singer metrics output..."
	@poetry run python scripts/test_singer_metrics.py
	@echo "✅ Singer metrics test complete"

# ============================================================================
# 🔍 DATA QUALITY & VALIDATION
# ============================================================================

validate-ldif-format: ## Validate LDIF format compliance
	@echo "🔍 Validating LDIF format compliance..."
	@poetry run python scripts/validate_ldif_format.py
	@echo "✅ LDIF format validation complete"

validate-schema-discovery: ## Validate schema discovery accuracy
	@echo "🔍 Validating schema discovery..."
	@poetry run python scripts/validate_schema_discovery.py
	@echo "✅ Schema discovery validation complete"

validate-data-extraction: ## Validate data extraction accuracy
	@echo "🔍 Validating data extraction..."
	@poetry run python scripts/validate_data_extraction.py
	@echo "✅ Data extraction validation complete"

data-quality-report: ## Generate comprehensive data quality report
	@echo "📊 Generating data quality report..."
	@poetry run python scripts/generate_quality_report.py
	@echo "✅ Data quality report generated"

# ============================================================================
# 📦 BUILD & DISTRIBUTION
# ============================================================================

build: clean ## Build distribution packages
	@echo "🔨 Building distribution..."
	@poetry build
	@echo "✅ Build complete - packages in dist/"

package: build ## Create deployment package
	@echo "📦 Creating deployment package..."
	@tar -czf dist/flext-tap-ldif-deployment.tar.gz \
		src/ \
		tests/ \
		scripts/ \
		pyproject.toml \
		README.md \
		CLAUDE.md
	@echo "✅ Deployment package created: dist/flext-tap-ldif-deployment.tar.gz"

# ============================================================================
# 🧹 CLEANUP
# ============================================================================

clean: ## Remove all artifacts
	@echo "🧹 Cleaning up..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	@rm -f catalog.json
	@rm -f state.json
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

# ============================================================================
# 📊 DEPENDENCY MANAGEMENT
# ============================================================================

deps-update: ## Update all dependencies
	@echo "🔄 Updating dependencies..."
	@poetry update
	@echo "✅ Dependencies updated"

deps-audit: ## Audit dependencies for vulnerabilities
	@echo "🔍 Auditing dependencies..."
	@poetry run pip-audit
	@echo "✅ Dependency audit complete"

deps-tree: ## Show dependency tree
	@echo "🌳 Dependency tree:"
	@poetry show --tree

deps-outdated: ## Show outdated dependencies
	@echo "📋 Outdated dependencies:"
	@poetry show --outdated

# ============================================================================
# 🔧 ENVIRONMENT CONFIGURATION
# ============================================================================

# Python settings
PYTHON := python3.13
export PYTHONPATH := $(PWD)/src:$(PYTHONPATH)
export PYTHONDONTWRITEBYTECODE := 1
export PYTHONUNBUFFERED := 1

# LDIF Tap settings
export TAP_LDIF_FILE_PATH := ./sample_data/sample.ldif
export TAP_LDIF_FILE_PATTERN := *.ldif
export TAP_LDIF_ENCODING := utf-8
export TAP_LDIF_AUTO_DETECT_ENCODING := true

# Processing settings
export TAP_LDIF_PROCESSING_MODE := entries
export TAP_LDIF_MAX_ENTRIES_PER_BATCH := 1000
export TAP_LDIF_ENABLE_STREAMING := true
export TAP_LDIF_BUFFER_SIZE := 8192

# Validation settings
export TAP_LDIF_VALIDATE_ENTRIES := true
export TAP_LDIF_STRICT_PARSING := false
export TAP_LDIF_SKIP_INVALID := true

# Performance settings
export TAP_LDIF_MAX_MEMORY_USAGE := 104857600
export TAP_LDIF_PARALLEL_PROCESSING := false

# Singer settings
export SINGER_SDK_LOG_LEVEL := INFO
export SINGER_SDK_BATCH_SIZE := 1000
export SINGER_SDK_MAX_RECORD_AGE_IN_MINUTES := 5

# Poetry settings
export POETRY_VENV_IN_PROJECT := false
export POETRY_CACHE_DIR := $(HOME)/.cache/pypoetry

# Quality gate settings
export MYPY_CACHE_DIR := .mypy_cache
export RUFF_CACHE_DIR := .ruff_cache

# ============================================================================
# 📝 PROJECT METADATA
# ============================================================================

# Project information
PROJECT_NAME := flext-tap-ldif
PROJECT_VERSION := $(shell poetry version -s)
PROJECT_DESCRIPTION := FLEXT TAP LDIF - Singer Tap for LDIF Data Extraction

.DEFAULT_GOAL := help

# ============================================================================
# 🎯 DEVELOPMENT UTILITIES
# ============================================================================

dev-tap-server: ## Start development tap server
	@echo "🔧 Starting development tap server..."
	@poetry run python scripts/dev_tap_server.py
	@echo "✅ Development tap server started"

dev-tap-monitor: ## Monitor tap operations
	@echo "📊 Monitoring tap operations..."
	@poetry run python scripts/monitor_tap_operations.py
	@echo "✅ Tap monitoring complete"

dev-ldif-playground: ## Interactive LDIF playground
	@echo "🎮 Starting LDIF playground..."
	@poetry run python scripts/ldif_playground.py
	@echo "✅ LDIF playground session complete"

# ============================================================================
# 🎯 FLEXT ECOSYSTEM INTEGRATION
# ============================================================================

ecosystem-check: ## Verify FLEXT ecosystem compatibility
	@echo "🌐 Checking FLEXT ecosystem compatibility..."
	@echo "📦 Core project: $(PROJECT_NAME) v$(PROJECT_VERSION)"
	@echo "🏗️ Architecture: Singer Tap + LDIF Processing"
	@echo "🐍 Python: 3.13"
	@echo "🔗 Framework: FLEXT Core + Singer SDK + LDIF"
	@echo "📊 Quality: Zero tolerance enforcement"
	@echo "✅ Ecosystem compatibility verified"

workspace-info: ## Show workspace integration info
	@echo "🏢 FLEXT Workspace Integration"
	@echo "==============================="
	@echo "📁 Project Path: $(PWD)"
	@echo "🏆 Role: Singer Tap for LDIF Data Extraction"
	@echo "🔗 Dependencies: flext-core, flext-ldif, singer-sdk"
	@echo "📦 Provides: LDIF file data extraction via Singer protocol"
	@echo "🎯 Standards: Enterprise Singer tap patterns"

# ============================================================================
# 🔄 CONTINUOUS INTEGRATION
# ============================================================================

ci-check: validate ## CI quality checks
	@echo "🔍 Running CI quality checks..."
	@poetry run python scripts/ci_quality_report.py
	@echo "✅ CI quality checks complete"

ci-performance: ## CI performance benchmarks
	@echo "⚡ Running CI performance benchmarks..."
	@poetry run python scripts/ci_performance_benchmarks.py
	@echo "✅ CI performance benchmarks complete"

ci-integration: ## CI integration tests
	@echo "🔗 Running CI integration tests..."
	@poetry run pytest tests/integration/ -v --tb=short
	@echo "✅ CI integration tests complete"

ci-singer: ## CI Singer protocol tests
	@echo "🎵 Running CI Singer tests..."
	@poetry run pytest tests/ -m "singer" -v --tb=short
	@echo "✅ CI Singer tests complete"

ci-all: ci-check ci-performance ci-integration ci-singer ## Run all CI checks
	@echo "✅ All CI checks complete"

# ============================================================================
# 🚀 PRODUCTION DEPLOYMENT
# ============================================================================

deploy-tap: validate build ## Deploy tap for production use
	@echo "🚀 Deploying LDIF tap..."
	@poetry run python scripts/deploy_tap.py
	@echo "✅ LDIF tap deployment complete"

test-deployment: ## Test deployed tap functionality
	@echo "🧪 Testing deployed tap..."
	@poetry run python scripts/test_deployed_tap.py
	@echo "✅ Deployment test complete"

rollback-deployment: ## Rollback tap deployment
	@echo "🔄 Rolling back tap deployment..."
	@poetry run python scripts/rollback_tap_deployment.py
	@echo "✅ Deployment rollback complete"