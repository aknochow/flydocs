"""Tests for the linter."""

from __future__ import annotations

from datetime import date

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
            "---\ntype: Guide\ntitle: X\ndescription: Y\n---\n[Link](nonexistent.md)\n"
        )
        config = Config(docs_dir=str(docs))
        assert lint(config) == 1

    def test_warns_invalid_status(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text(
            "---\ntype: Guide\ntitle: X\ndescription: Y\nstatus: archived\n---\n# X\n"
        )
        config = Config(docs_dir=str(docs))
        assert lint(config) == 0
        assert lint(config, strict=True) == 1

    def test_ok_draft_status_is_valid(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text(
            "---\ntype: Guide\ntitle: X\ndescription: Y\nstatus: draft\n---\n# X\n"
        )
        config = Config(docs_dir=str(docs))
        assert lint(config, strict=True) == 0

    def test_warns_stale_doc(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text(
            "---\ntype: Guide\ntitle: X\ndescription: Y\nstale_after: 2020-01-01\n---\n# X\n"
        )
        config = Config(docs_dir=str(docs))
        assert lint(config, today=date(2026, 1, 1)) == 0
        assert lint(config, strict=True, today=date(2026, 1, 1)) == 1

    def test_stale_after_future_does_not_warn(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text(
            "---\ntype: Guide\ntitle: X\ndescription: Y\nstale_after: 2099-01-01\n---\n# X\n"
        )
        config = Config(docs_dir=str(docs))
        assert lint(config, strict=True, today=date(2026, 1, 1)) == 0

    def test_warns_malformed_stale_after_date(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text(
            "---\ntype: Guide\ntitle: X\ndescription: Y\nstale_after: not-a-date\n---\n# X\n"
        )
        config = Config(docs_dir=str(docs))
        assert lint(config, strict=True) == 1

    def test_warns_missing_generated_by(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text(
            "---\ntype: Guide\ntitle: X\ndescription: Y\ngenerated:\n  at: 2026-01-01\n---\n# X\n"
        )
        config = Config(docs_dir=str(docs))
        assert lint(config, strict=True) == 1

    def test_ok_generated_with_by(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text(
            "---\ntype: Guide\ntitle: X\ndescription: Y\n"
            "generated:\n  by: human:x\n  at: 2026-01-01\n---\n# X\n"
        )
        config = Config(docs_dir=str(docs))
        assert lint(config, strict=True) == 0

    def test_warns_verified_entry_missing_by(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text(
            "---\ntype: Guide\ntitle: X\ndescription: Y\nverified:\n  at: 2026-01-01\n---\n# X\n"
        )
        config = Config(docs_dir=str(docs))
        assert lint(config, strict=True) == 1

    def test_ok_verified_bare_mapping_shorthand(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text(
            "---\ntype: Guide\ntitle: X\ndescription: Y\n"
            "verified:\n  by: human:x\n  at: 2026-01-01\n---\n# X\n"
        )
        config = Config(docs_dir=str(docs))
        assert lint(config, strict=True) == 0

    def test_warns_sources_missing_resource(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text(
            "---\ntype: Guide\ntitle: X\ndescription: Y\n"
            "sources:\n  - title: Some Source\n---\n# X\n"
        )
        config = Config(docs_dir=str(docs))
        assert lint(config, strict=True) == 1

    def test_ok_sources_with_resource(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "page.md").write_text(
            "---\ntype: Guide\ntitle: X\ndescription: Y\n"
            "sources:\n  - resource: src/foo.py\n---\n# X\n"
        )
        config = Config(docs_dir=str(docs))
        assert lint(config, strict=True) == 0
