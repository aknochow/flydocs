"""Flydocs CLI — static documentation sites with PatternFly."""

from __future__ import annotations

import sys

import click

from flydocs import __version__
from flydocs.config import load_config


@click.group()
@click.version_option(version=__version__, prog_name="flydocs")
def main():
    """Static documentation sites with PatternFly from markdown."""


@main.command()
@click.option("--config", "config_path", default=None, help="Config file path.")
@click.option("--clean/--no-clean", default=False, help="Remove site_dir before building.")
def build(config_path, clean):
    """Build the documentation site."""
    from flydocs.builder import build_site

    config = load_config(config_path)
    build_site(config, clean=clean)


@main.command()
@click.option("--port", default=8000, type=int, help="Port to serve on.")
@click.option("--config", "config_path", default=None, help="Config file path.")
def preview(port, config_path):
    """Build and preview the site locally."""
    from flydocs.server import preview as do_preview

    config = load_config(config_path)
    do_preview(config, port=port)


@main.command()
@click.option("--config", "config_path", default=None, help="Config file path.")
@click.option("--strict/--no-strict", default=False, help="Treat warnings as errors.")
def lint(config_path, strict):
    """Validate frontmatter, navigation, and links."""
    from flydocs.linter import lint as do_lint

    config = load_config(config_path)
    sys.exit(do_lint(config, strict=strict))


@main.command()
@click.argument("query")
@click.option("--config", "config_path", default=None, help="Config file path.")
def search(query, config_path):
    """Search documentation by title, description, and tags."""
    from flydocs.search import search as do_search

    config = load_config(config_path)
    do_search(query, config)


@main.command()
@click.argument("path")
@click.option(
    "--type",
    "doc_type",
    default="Guide",
    type=click.Choice(["Concept", "Guide", "Reference", "Example"]),
    help="OKF document type.",
)
def init(path, doc_type):
    """Scaffold a new markdown document with OKF frontmatter."""
    import os

    if os.path.exists(path):
        click.echo(f"Error: {path} already exists", err=True)
        sys.exit(1)

    name = os.path.basename(path).replace(".md", "").replace("-", " ").title()
    content = f"""---
type: {doc_type}
title: {name}
description: TODO
tags: []
---

# {name}

TODO: Write documentation.
"""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    click.echo(f"Created {path}")


@main.command()
@click.option("--config", "config_path", default=None, help="Config file path.")
def badges(config_path):
    """Print badge markdown for README."""
    from flydocs.badges import badges_markdown

    config = load_config(config_path)
    md = badges_markdown(config.badges)
    if md:
        click.echo(md)
    else:
        click.echo("No badges configured.", err=True)


@main.command()
@click.option("--config", "config_path", default=None, help="Config file path.")
@click.option("--output", "-o", default="README.md", help="Output file path.")
@click.option("--dry-run", is_flag=True, help="Print to stdout instead of writing.")
def readme(config_path, output, dry_run):
    """Generate README.md from docs/index.md."""
    from flydocs.readme import generate_readme

    config = load_config(config_path)
    content = generate_readme(config)
    if dry_run:
        click.echo(content)
    else:
        with open(output, "w") as f:
            f.write(content)
        click.echo(f"Generated {output}")


@main.group()
def okf():
    """OKF migration tools."""


@okf.command("preview")
@click.option("--config", "config_path", default=None, help="Config file path.")
@click.option("--output", default="public-okf", help="Output directory for preview.")
def okf_preview(config_path, output):
    """Build OKF-enhanced preview without modifying source."""
    from flydocs.okf import okf_preview as do_preview

    config = load_config(config_path)
    do_preview(config, output_dir=output)


@okf.command("init")
@click.argument("path", default="docs/")
def okf_init(path):
    """Scaffold OKF frontmatter onto existing docs."""
    from flydocs.okf import okf_init as do_init

    do_init(path)
