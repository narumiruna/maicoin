set dotenv-load := true

[default]
all: format lint type test

# Format code using ruff
format:
    uv run ruff format

# Lint code using ruff
lint:
    uv run ruff check --fix

# Type checking using ty
type:
    uv run ty check

# Run tests using pytest with coverage
test:
    uv run pytest -v -s --cov=src tests

# Run live integration tests against the real MAX API
live-test:
    RUN_LIVE_TESTS=1 uv run pytest -v -s -m live tests/live

# Build and publish the package to PyPI
publish:
    uv build
    uv publish

# Serve the documentation locally with live reload
docs-serve:
    uv run --group docs mkdocs serve

# Build the static documentation site into ./site
docs-build:
    uv run --group docs mkdocs build --strict
