# Makefile for OracleDBA

.PHONY: help install install-dev test lint format clean build upload docs

help:
	@echo "OracleDBA - Oracle Database Administration Package"
	@echo ""
	@echo "Available targets:"
	@echo "  install      - Install package"
	@echo "  install-dev  - Install package in development mode"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linter (flake8)"
	@echo "  format       - Format code (black)"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build distribution packages"
	@echo "  upload       - Upload to PyPI"
	@echo "  docs         - Generate documentation"

install:
	pip install .

install-dev:
	pip install -e .[dev]

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=oracledba --cov-report=html

lint:
	flake8 oracledba/ tests/ --max-line-length=100

format:
	black oracledba/ tests/ --line-length=100

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python setup.py sdist bdist_wheel

upload: build
	twine upload dist/*

upload-test: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

docs:
	cd docs && make html

# Development shortcuts
dev-setup: install-dev
	@echo "Development environment ready!"

quick-test:
	pytest tests/ -v -x

watch:
	ptw tests/ oracledba/ -- -v

# Package info
info:
	@echo "Package: oracledba"
	@echo "Version: 1.0.0"
	@python --version
	@pip --version
