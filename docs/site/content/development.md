# 🛠️ Development

This repo uses [uv](https://docs.astral.sh/uv/) for dependency management and [just](https://github.com/casey/just) as a task runner.

## Setup

```shell
uv sync
```

## Common tasks

```shell
just            # format, lint, type-check, test
just format     # ruff format
just lint       # ruff check --fix
just type       # ty check
just test       # pytest with coverage
just live-test  # live integration tests against the real MAX API
```

## Documentation

The site you're reading is built with [MkDocs](https://www.mkdocs.org/) and the [Material theme](https://squidfunk.github.io/mkdocs-material/). API pages are generated from docstrings via [mkdocstrings](https://mkdocstrings.github.io/).

```shell
just docs-serve   # live preview at http://127.0.0.1:8000
just docs-build   # build the static site into docs/site/build
```

Docs deploy automatically to GitHub Pages on every push to `main` via `.github/workflows/docs.yml`.

## Project layout

```text
src/maicoin/
  v3/         # REST v3 client, models, auth helpers, errors
  ws/         # WebSocket stream client and channel models
tests/
  v3/, ws/    # unit tests with mocked sessions
  live/      # live integration tests (skipped by default)
docs/
  site/      # MkDocs config, source, and generated build output
  plans/     # active coding-agent plans and archived notes
examples/     # runnable scripts using the real API
```

## Releasing

`bump-my-version` is configured via `pyproject.toml`. To cut a release:

```shell
uv run bump-my-version bump <patch|minor|major>
git push --follow-tags
```

The publish workflow uploads to PyPI on tag pushes; the docs workflow republishes the site on push to `main`.
