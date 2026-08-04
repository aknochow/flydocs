"""Tests for the build pipeline."""

from __future__ import annotations

import os

import pytest

from flydocs.builder import _validate_site_dir, build_site, collect_md_files
from flydocs.config import Config


class TestCollectMdFiles:
    def test_finds_files(self, tmp_docs):
        files = collect_md_files(str(tmp_docs))
        assert "index.md" in files
        assert "guides/quickstart.md" in files

    def test_sorted_order(self, tmp_docs):
        (tmp_docs / "zebra.md").write_text("---\ntype: Guide\ntitle: Z\ndescription: Z\n---\n# Z\n")
        (tmp_docs / "alpha.md").write_text("---\ntype: Guide\ntitle: A\ndescription: A\n---\n# A\n")
        files = collect_md_files(str(tmp_docs))
        md_only = [f for f in files if "/" not in f]
        assert md_only == sorted(md_only)

    def test_empty_dir(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        assert collect_md_files(str(empty)) == []


class TestValidateSiteDir:
    def test_valid_relative(self):
        _validate_site_dir("public")

    def test_escaping_path_exits(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(SystemExit, match="escapes project root"):
            _validate_site_dir("/tmp")


class TestBuildSite:
    def test_builds_pages(self, sample_config, monkeypatch):
        monkeypatch.chdir(os.path.dirname(sample_config.docs_dir))
        build_site(sample_config)
        assert os.path.exists(os.path.join(sample_config.site_dir, "index.html"))
        assert os.path.exists(
            os.path.join(sample_config.site_dir, "guides", "quickstart", "index.html")
        )

    def test_copies_assets(self, sample_config, monkeypatch):
        monkeypatch.chdir(os.path.dirname(sample_config.docs_dir))
        build_site(sample_config)
        assert os.path.exists(os.path.join(sample_config.site_dir, "assets", "css", "flydocs.css"))
        assert os.path.exists(os.path.join(sample_config.site_dir, "assets", "js", "flydocs.js"))

    def test_clean_build(self, sample_config, monkeypatch):
        monkeypatch.chdir(os.path.dirname(sample_config.docs_dir))
        build_site(sample_config)
        marker = os.path.join(sample_config.site_dir, "stale.txt")
        with open(marker, "w") as f:
            f.write("stale")
        build_site(sample_config, clean=True)
        assert not os.path.exists(marker)

    def test_html_content(self, sample_config, monkeypatch):
        monkeypatch.chdir(os.path.dirname(sample_config.docs_dir))
        build_site(sample_config)
        with open(os.path.join(sample_config.site_dir, "index.html")) as f:
            html = f.read()
        assert "Test Project" in html
        assert "pf-v6-c-nav" in html
        assert "flydocs.css" in html

    def test_okf_v2_indicators_rendered(self, tmp_path, monkeypatch):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "index.md").write_text(
            "---\n"
            "type: Guide\n"
            "title: Draft Page\n"
            "description: A draft page.\n"
            "status: draft\n"
            "stale_after: 2020-01-01\n"
            "generated:\n"
            "  by: human:aknochow\n"
            "  at: 2026-01-01T00:00:00\n"
            "---\n\n"
            "# Draft Page\n"
        )
        config = Config(
            name="Draft Project",
            docs_dir=str(docs),
            site_dir=str(tmp_path / "public"),
        )
        monkeypatch.chdir(tmp_path)
        build_site(config)
        with open(os.path.join(config.site_dir, "index.html")) as f:
            html = f.read()
        assert "flydocs-status-label" in html
        assert ">draft<" in html
        assert "flydocs-stale-notice" in html
        assert "Last updated" in html
