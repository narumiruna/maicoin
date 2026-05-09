# Repository Guidelines

## Project Structure & Module Organization

This repository is a Python package for the MaiCoin MAX API. Core package code lives under `src/maicoin/`:

- `src/maicoin/ws/` contains WebSocket models, requests, responses, subscriptions, and stream helpers.
- `src/maicoin/v3/` contains HTTP API-related modules.
- `tests/` mirrors package areas, with current coverage focused on `tests/ws/` and `tests/v3/`.
- `examples/` contains runnable scripts (`rest.py`, `websocket.py`) that load MAX credentials from `.env` and exercise the package locally.
- `.agents/docs/` is for coding-agent-authored working documents: put finished plans or notes in `.agents/docs/archived/`, unfinished implementation plans in `.agents/docs/plans/`, and future follow-up items in `.agents/docs/TODO.md`.

## Build, Test, and Development Commands

Use uv for dependency management and `just` for project tasks. The default recipe runs the full local gate:

```shell
uv sync
just          # runs format, lint, type, and test
just format   # uv run ruff format
just lint     # uv run ruff check --fix
just type     # uv run ty check
just test     # uv run pytest -v -s --cov=src tests
just publish  # uv build; uv publish
```

For a quick local package check, run:

```shell
uv run python examples/rest.py
uv run python examples/websocket.py
```

## Coding Style & Naming Conventions

Target Python 3.12+. Ruff is the primary linter; keep lines at or below 120 characters. Ruff enforces pycodestyle, pyflakes, isort, pep8-naming, pyupgrade, flake8-bugbear, and flake8-comprehensions rules. Imports should be sorted with one import per line. Keep public models and request/response classes named clearly after MAX API concepts, matching existing files such as `ticker.py`, `order.py`, and `subscription.py`.

## Testing Guidelines

Use pytest. Place tests under `tests/` using `test_*.py` filenames and mirror the package path when adding new modules. Prefer deterministic unit tests for serialization, parsing, validation, and request construction. Run `just test` for the standard coverage command, or `just` before submitting broader changes.

## API Reference Links

When implementing or reviewing API behavior, consult the official MAX documentation first:

- HTTP API v3: https://max-api.maicoin.com/doc/v3.html
- WebSocket API: https://maicoin.github.io/max-websocket-docs/

Keep naming, payload fields, channel names, and authentication behavior aligned with those references.

## Commit & Pull Request Guidelines

Recent history uses short imperative or dependency-update messages, often from Dependabot. Keep commits focused and descriptive, for example `Add websocket ticker parsing tests` or `Bump actions/checkout from 4 to 5`. Pull requests should include a summary, test results, and links to related issues or API documentation when behavior changes.

## Security & Configuration Tips

Do not commit `.env` files, API keys, or secrets. Use `MAX_API_KEY` and `MAX_API_SECRET` only through local environment variables or ignored local configuration.
