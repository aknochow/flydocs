"""Shared test fixtures."""

from __future__ import annotations


import pytest

from flydocs.config import Badge, Config


@pytest.fixture
def tmp_docs(tmp_path):
    """Create a temporary docs directory with sample markdown files."""
    docs = tmp_path / "docs"
    docs.mkdir()

    (docs / "index.md").write_text(
        "---\n"
        "type: Guide\n"
        "title: Test Project\n"
        "description: A test project.\n"
        "tags: [test]\n"
        "---\n\n"
        "# Test Project\n\n"
        "Welcome to the test project.\n"
    )

    guides = docs / "guides"
    guides.mkdir()
    (guides / "quickstart.md").write_text(
        "---\n"
        "type: Guide\n"
        "title: Quickstart\n"
        "description: Get started fast.\n"
        "tags: [quickstart]\n"
        "---\n\n"
        "# Quickstart\n\n"
        "See [home](../index.md) for more.\n"
    )

    return docs


@pytest.fixture
def sample_config(tmp_docs):
    """Create a Config pointing at the temp docs directory."""
    return Config(
        name="Test Project",
        url="https://example.com/docs/",
        docs_dir=str(tmp_docs),
        site_dir=str(tmp_docs.parent / "public"),
        nav=(
            {"Overview": [{"Introduction": "index.md"}]},
            {"Guides": [{"Quickstart": "guides/quickstart.md"}]},
        ),
    )


@pytest.fixture
def sample_badges():
    """Sample badge tuple for testing."""
    return (
        Badge(id="version", label="v1.0", url="https://example.com/releases", img="https://img.shields.io/badge/v1.0-blue"),
        Badge(id="docs", label="Docs", url="https://example.com/docs/", img="https://img.shields.io/badge/docs-green"),
    )
