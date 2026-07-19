"""Tests for the linter."""

from __future__ import annotations

from flydocs.config import Config
from flydocs.linter import lint


class TestLint:
    def test_passes_valid_docs(self, sample_config):
        assert lint(sample_config) == 0

    def test_fails_missing_frontmatter(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "bad.md").write_text("# No frontmatter\n")
        config = Config(docs_dir=str(docs))
        assert lint(config) == 1

    def test_fails_missing_type(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "bad.md").write_text("---\ntitle: X\ndescription: Y\n---\n# X\n")
        config = Config(docs_dir=str(docs))
        assert lint(config) == 1

    def test_fails_missing_title(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "bad.md").write_text("---\ntype: Guide\ndescription: Y\n---\n# X\n")
        config = Config(docs_dir=str(docs))
        assert lint(config) == 1

    def test_warns_unknown_type(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text("---\ntype: Runbook\ntitle: X\ndescription: Y\n---\n# X\n")
        config = Config(docs_dir=str(docs))
        assert lint(config) == 0
        assert lint(config, strict=True) == 1

    def test_warns_not_in_nav(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "orphan.md").write_text("---\ntype: Guide\ntitle: X\ndescription: Y\n---\n# X\n")
        config = Config(
            docs_dir=str(docs),
            nav=({"Main": [{"Other": "other.md"}]},),
        )
        assert lint(config) == 1  # nav entry missing on disk

    def test_fails_broken_link(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text(
            "---\ntype: Guide\ntitle: X\ndescription: Y\n---\n"
            "[Link](nonexistent.md)\n"
        )
        config = Config(docs_dir=str(docs))
        assert lint(config) == 1
