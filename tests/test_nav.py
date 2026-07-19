"""Tests for navigation loading and sidebar generation."""

from __future__ import annotations

from flydocs.config import SidebarConfig
from flydocs.nav import build_sidebar, load_nav


class TestLoadNav:
    def test_basic(self):
        raw = ({"Overview": [{"Home": "index.md"}]},)
        nav = load_nav(raw)
        assert len(nav) == 1
        assert nav[0]["title"] == "Overview"
        assert nav[0]["entries"][0]["label"] == "Home"
        assert nav[0]["entries"][0]["file"] == "index.md"

    def test_empty_section_skipped(self):
        raw = ({"Empty": []},)
        nav = load_nav(raw)
        assert len(nav) == 0

    def test_multiple_sections(self):
        raw = (
            {"Overview": [{"Home": "index.md"}]},
            {"Guides": [{"Start": "guides/start.md"}]},
        )
        nav = load_nav(raw)
        assert len(nav) == 2


class TestBuildSidebar:
    def test_renders_html(self):
        nav = [{"title": "Overview", "entries": [{"label": "Home", "path": "", "file": "index.md"}]}]
        html = build_sidebar(nav, "index.md")
        assert "pf-v6-c-nav" in html
        assert "pf-m-current" in html
        assert "Home" in html

    def test_escapes_html(self):
        nav = [{"title": "Q&A", "entries": [{"label": "<b>Bold</b>", "path": "qa", "file": "qa.md"}]}]
        html = build_sidebar(nav, "other.md")
        assert "Q&amp;A" in html
        assert "&lt;b&gt;Bold&lt;/b&gt;" in html

    def test_sidebar_config_expanded(self):
        nav = [
            {"title": "A", "entries": [{"label": "P1", "path": "a", "file": "a.md"}]},
            {"title": "B", "entries": [{"label": "P2", "path": "b", "file": "b.md"}]},
        ]
        config = SidebarConfig(expanded=True)
        html = build_sidebar(nav, "other.md", sidebar_config=config)
        assert html.count(" open") == 2

    def test_sidebar_config_collapsed(self):
        nav = [
            {"title": "A", "entries": [{"label": "P1", "path": "a", "file": "a.md"}]},
            {"title": "B", "entries": [{"label": "P2", "path": "b", "file": "b.md"}]},
        ]
        config = SidebarConfig(expanded=False)
        html = build_sidebar(nav, "other.md", sidebar_config=config)
        assert " open" not in html

    def test_sidebar_overrides(self):
        nav = [
            {"title": "A", "entries": [{"label": "P1", "path": "a", "file": "a.md"}]},
            {"title": "B", "entries": [{"label": "P2", "path": "b", "file": "b.md"}]},
        ]
        config = SidebarConfig(expanded=True, overrides={"B": False})
        html = build_sidebar(nav, "other.md", sidebar_config=config)
        assert html.count(" open") == 1

    def test_active_section_always_open(self):
        nav = [{"title": "A", "entries": [{"label": "P1", "path": "a", "file": "a.md"}]}]
        config = SidebarConfig(expanded=False)
        html = build_sidebar(nav, "a.md", sidebar_config=config)
        assert " open" in html
