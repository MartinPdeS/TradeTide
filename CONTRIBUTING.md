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

The root ``Makefile`` provides matching shortcuts: ``make quick`` configures,
builds, and installs the native extensions; ``make editable`` bootstraps the
declared build backend before its editable install; ``make test`` runs tests
with a headless Matplotlib backend; and ``make quality`` runs the focused lint
and type checks. Set ``PYTHON`` or ``BUILD_DIR`` to override their defaults.

Release tags use ``vMAJOR.MINOR.PATCH``. ``make tag VERSION=vX.Y.Z`` regenerates
the explicit version file, creates a release commit, and makes an annotated tag
without pushing. ``make release patch``, ``make release minor``, and ``make
release major`` derive the next version and push the release commit and tag.

## Pull requests

- Keep each change focused and add tests for changed public behavior.
- Use deterministic test inputs; do not rely on random values without a seeded generator.
- Document public APIs and add an entry under **Unreleased** in `CHANGELOG.md`.
- Do not commit compiled extension modules, build directories, coverage reports, or local virtual environments.

## Shared release versioning

Versions are explicit in `[project].version`; builds never derive versions from
Git. Install the pinned release tool in the interpreter used by Make:

```sh
python -m pip install "martinpdes-maintenance==0.2.2"
make release-check PYTHON=python
```

The `release` extra declares the same tool. The Makefile calls the installed module directly, and
`[tool.mps-maintenance]` declares the package's release files. Use
`python -m martinpdes_maintenance.cli tag vX.Y.Z --dry-run` to preview changes from a clean,
full checkout. The tool aligns configured metadata, commits, and creates an
annotated tag; it never pushes. Existing Makefile publishing shortcuts retain
their push behavior. Fetch remote tags first. With no release tags, `next` uses
the explicit project version as its starting point.
