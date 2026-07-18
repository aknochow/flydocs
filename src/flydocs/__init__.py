"""Flydocs — static documentation sites with PatternFly from markdown."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("flydocs")
except PackageNotFoundError:
    __version__ = "0.0.0"
