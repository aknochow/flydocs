"""OKF migration tools — preview and init."""

from __future__ import annotations

import click

from flydocs.config import Config


def okf_preview(config: Config, output_dir: str = "public-okf") -> None:
    """Generate an OKF-enhanced preview build without modifying source files."""
    click.echo("OKF preview is not yet implemented.", err=True)
    raise SystemExit(1)


def okf_init(path: str) -> None:
    """Scaffold OKF frontmatter onto existing markdown files."""
    click.echo("OKF init is not yet implemented.", err=True)
    raise SystemExit(1)
