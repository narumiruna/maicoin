# Repository Guidelines

## Project Structure & Module Organization

This repository is a Python package for the MaiCoin MAX API. Core package code lives under `maicoin/`:

- `maicoin/ws/` contains WebSocket models, requests, responses, subscriptions, and stream helpers.
- `maicoin/v2/` contains HTTP API-related modules.
- `tests/` mirrors package areas, with current coverage focused on `tests/ws/`.
- `example.py` demonstrates loading MAX credentials from `.env` and running the package locally.

## Build, Test, and Development Commands

Use Poetry for dependency management:

```shell
poetry install
poetry run pytest
poetry run pytest --cov=maicoin
poetry run ruff check .
```

For a quick local package check, run:

```shell
pip install .
python example.py
```

## Coding Style & Naming Conventions

Target Python 3.10+. Ruff is the primary linter; keep lines at or below 120 characters. Ruff enforces pycodestyle, pyflakes, isort, pep8-naming, pyupgrade, flake8-bugbear, and flake8-comprehensions rules. Imports should be sorted with one import per line. Keep public models and request/response classes named clearly after MAX API concepts, matching existing files such as `ticker.py`, `order.py`, and `subscription.py`.

## Testing Guidelines

Use pytest. Place tests under `tests/` using `test_*.py` filenames and mirror the package path when adding new modules. Prefer deterministic unit tests for serialization, parsing, validation, and request construction. Run `poetry run pytest` before submitting changes; use `poetry run pytest --cov=maicoin` when changing core API behavior.

## API Reference Links

When implementing or reviewing API behavior, consult the official MAX documentation first:

- HTTP API v3: https://max-api.maicoin.com/doc/v3.html
- WebSocket API: https://maicoin.github.io/max-websocket-docs/

Keep naming, payload fields, channel names, and authentication behavior aligned with those references.

## Commit & Pull Request Guidelines

Recent history uses short imperative or dependency-update messages, often from Dependabot. Keep commits focused and descriptive, for example `Add websocket ticker parsing tests` or `Bump actions/checkout from 4 to 5`. Pull requests should include a summary, test results, and links to related issues or API documentation when behavior changes.

## Security & Configuration Tips

Do not commit `.env` files, API keys, or secrets. Use `MAX_API_KEY` and `MAX_API_SECRET` only through local environment variables or ignored local configuration.
