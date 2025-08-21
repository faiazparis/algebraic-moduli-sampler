.PHONY: help setup install lint format typecheck test docs clean all

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup:  ## Install development dependencies and setup pre-commit
	pip install -e ".[dev]"
	pre-commit install

install:  ## Install the package in development mode
	pip install -e .

lint:  ## Run all linting checks
	ruff check .
	black --check .
	isort --check-only .

format:  ## Format code with black and isort
	black .
	isort .

typecheck:  ## Run mypy type checking
	mypy src/ tests/

test:  ## Run tests with coverage
	pytest --cov=src --cov-report=term-missing --cov-report=html

docs:  ## Build and serve documentation
	mkdocs serve

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

all: format lint typecheck test  ## Run all checks (format, lint, typecheck, test)
