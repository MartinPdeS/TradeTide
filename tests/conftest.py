"""Ensure wheel tests import the installed distribution, not the checkout."""

from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
import sys


def _prefer_installed_tradetide() -> None:
    """Remove the repository root from ``sys.path`` when a wheel is installed.

    cibuildwheel and reusable CI actions install a wheel before running pytest,
    but also invoke pytest from the project checkout.  Without this guard,
    Python imports the checkout's Python files first; its platform-specific
    extension modules are not present, so collection reports a misleading
    circular-import error.
    """
    try:
        installed = Path(
            distribution("TradeTide").locate_file("TradeTide/__init__.py")
        ).resolve()
    except PackageNotFoundError:
        return

    repository = Path(__file__).resolve().parents[1]
    if not installed.is_file() or installed == repository / "TradeTide/__init__.py":
        return

    sys.path[:] = [
        entry
        for entry in sys.path
        if Path(entry or ".").resolve() != repository
    ]


_prefer_installed_tradetide()
