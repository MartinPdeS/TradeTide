# Contributing to TradeTide

## Development setup

TradeTide includes native C++ extensions. Use Python 3.10 or later, CMake 3.20 or later, and a C++20 compiler. On macOS and Linux, OpenMP must also be available to CMake.

```console
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pre-commit install
```

Run the checks before opening a pull request:

```console
ruff check TradeTide tests
ruff format TradeTide tests
mypy TradeTide
pytest
```

## Pull requests

- Keep each change focused and add tests for changed public behavior.
- Use deterministic test inputs; do not rely on random values without a seeded generator.
- Document public APIs and add an entry under **Unreleased** in `CHANGELOG.md`.
- Do not commit compiled extension modules, build directories, coverage reports, or local virtual environments.
