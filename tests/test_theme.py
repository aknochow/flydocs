"""Tests for theme resolution and rendering."""

from __future__ import annotations

from flydocs.config import BannerConfig, Config, ThemeConfig
from flydocs.theme import _sanitize_palette, build_banner_html, render_page, resolve_html_classes


class TestSanitizePalette:
    def test_valid_palette(self):
        assert _sanitize_palette("flydocs-dark") == "flydocs-dark"

    def test_default(self):
        assert _sanitize_palette("default") == "default"

    def test_invalid_falls_back(self):
        assert _sanitize_palette('x" onload="alert(1)') == "default"

    def test_empty_falls_back(self):
        assert _sanitize_palette("") == "default"

    def test_uppercase_falls_back(self):
        assert _sanitize_palette("FlydocsDark") == "default"


class TestResolveHtmlClasses:
    def test_dark_mode(self):
        result = resolve_html_classes("dark", "default")
        assert "pf-v6-theme-dark" in result

    def test_light_mode(self):
        result = resolve_html_classes("light", "default")
        assert result == ""

    def test_dark_with_palette(self):
        result = resolve_html_classes("dark", "flydocs-dark")
        assert "pf-v6-theme-dark" in result
        assert "flydocs-palette-flydocs-dark" in result

    def test_no_mode_with_palette(self):
        result = resolve_html_classes("", "flydocs-dark")
        assert "flydocs-palette-flydocs-dark" in result
        assert "pf-v6-theme-dark" not in result


class TestBuildBannerHtml:
    def test_empty_text(self):
        config = Config(theme=ThemeConfig(banner=BannerConfig(text="")))
        assert build_banner_html(config) == ""

    def test_renders_banner(self):
        config = Config(theme=ThemeConfig(banner=BannerConfig(text="Beta warning", color="gold")))
        html = build_banner_html(config)
        assert "Beta warning" in html
        assert "pf-m-gold" in html
        assert "pf-v6-c-banner" in html

    def test_banner_with_url(self):
        config = Config(
            theme=ThemeConfig(banner=BannerConfig(text="Click here", url="https://example.com"))
        )
        html = build_banner_html(config)
        assert "https://example.com" in html
        assert "<a href=" in html

    def test_banner_escapes_html(self):
        config = Config(theme=ThemeConfig(banner=BannerConfig(text="<script>alert(1)</script>")))
        html = build_banner_html(config)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


class TestRenderPage:
    def test_renders_complete_page(self):
        config = Config(name="Test Site")
        html = render_page(
            content="<p>Hello</p>",
            title="Page Title",
            description="A test page",
            sidebar_html="<nav>sidebar</nav>",
            badges_html="",
            config=config,
        )
        assert "Page Title · Test Site" in html
        assert "<p>Hello</p>" in html
        assert "<nav>sidebar</nav>" in html
        assert "flydocs.css" in html

    def test_home_page_title(self):
        config = Config(name="Test Site")
        html = render_page(
            content="<p>Home</p>",
            title="Test Site",
            description="Home page",
            sidebar_html="",
            badges_html="",
            config=config,
        )
        assert "Test Site" in html
        assert " · " not in html.split("<title>")[1].split("</title>")[0]

    def test_includes_theme_dropdown(self):
        config = Config(name="Test", theme=ThemeConfig(mode="auto"))
        html = render_page("", "T", "", "", "", config)
        assert "theme-dropdown" in html
        assert "color-scheme-group" in html

    def test_dark_mode_has_class(self):
        config = Config(name="Test", theme=ThemeConfig(mode="dark"))
        html = render_page("", "T", "", "", "", config)
        assert "pf-v6-theme-dark" in html

    def test_github_url_rendered(self):
        config = Config(name="Test", github_url="https://github.com/test/repo")
        html = render_page("", "T", "", "", "", config)
        assert "github.com/test/repo" in html
        assert "flydocs-github-link" in html

    def test_sidebar_toggle_rendered(self):
        config = Config(name="Test")
        html = render_page("", "T", "", "", "", config)
        assert "sidebar-toggle" in html

    def test_doc_type_metadata(self):
        config = Config(name="Test")
        html = render_page("", "T", "", "", "", config, doc_type="Guide")
        assert 'content="Guide"' in html
        assert "data-pagefind-filter" in html
