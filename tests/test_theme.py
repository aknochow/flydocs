"""Tests for theme resolution and rendering."""

from __future__ import annotations

from flydocs.config import BannerConfig, Config, ThemeConfig
from flydocs.theme import (
    _sanitize_palette,
    build_banner_html,
    build_deprecated_notice_html,
    build_footer_meta_html,
    build_stale_notice_html,
    build_status_badge_html,
    render_page,
    resolve_html_classes,
)


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

    def test_new_okf_fields_default_to_nothing(self):
        config = Config(name="Test")
        html = render_page("<p>Body</p>", "T", "", "", "", config)
        assert "flydocs-doc-meta" not in html
        assert "flydocs-status-label" not in html
        assert "flydocs-deprecated-notice" not in html
        assert "flydocs-stale-notice" not in html

    def test_status_badge_rendered(self):
        config = Config(name="Test")
        html = render_page("", "T", "", "", "", config, status="draft")
        assert "flydocs-doc-meta" in html
        assert "flydocs-status-label" in html
        assert ">draft<" in html

    def test_deprecated_notice_rendered(self):
        config = Config(name="Test")
        html = render_page("", "T", "", "", "", config, status="deprecated")
        assert "flydocs-deprecated-notice" in html
        assert "deprecated" in html.lower()

    def test_stale_notice_rendered(self):
        config = Config(name="Test")
        html = render_page("", "T", "", "", "", config, stale_after="2020-01-01")
        assert "flydocs-stale-notice" in html
        assert "2020-01-01" in html

    def test_footer_meta_rendered(self):
        config = Config(name="Test")
        html = render_page("", "T", "", "", "", config, generated_at="2026-01-01T00:00:00")
        assert "Last updated 2026-01-01T00:00:00" in html


class TestBuildStatusBadgeHtml:
    def test_stable_renders_nothing(self):
        assert build_status_badge_html("stable") == ""

    def test_empty_renders_nothing(self):
        assert build_status_badge_html("") == ""

    def test_draft_renders_badge(self):
        html = build_status_badge_html("draft")
        assert "flydocs-status-label" in html
        assert "flydocs-status-warning" in html
        assert ">draft<" in html

    def test_deprecated_renders_badge(self):
        html = build_status_badge_html("deprecated")
        assert "flydocs-status-danger" in html
        assert ">deprecated<" in html

    def test_escapes_html(self):
        html = build_status_badge_html("draft")
        assert "<script>" not in html


class TestBuildDeprecatedNoticeHtml:
    def test_non_deprecated_renders_nothing(self):
        assert build_deprecated_notice_html("draft") == ""
        assert build_deprecated_notice_html("stable") == ""
        assert build_deprecated_notice_html("") == ""

    def test_deprecated_renders_notice(self):
        html = build_deprecated_notice_html("deprecated")
        assert "flydocs-deprecated-notice" in html
        assert "deprecated" in html.lower()


class TestBuildStaleNoticeHtml:
    def test_empty_renders_nothing(self):
        assert build_stale_notice_html("") == ""

    def test_renders_notice_with_date(self):
        html = build_stale_notice_html("2020-01-01")
        assert "flydocs-stale-notice" in html
        assert "2020-01-01" in html

    def test_escapes_html(self):
        html = build_stale_notice_html("<script>alert(1)</script>")
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


class TestBuildFooterMetaHtml:
    def test_empty_renders_nothing(self):
        assert build_footer_meta_html("") == ""

    def test_renders_last_updated(self):
        html = build_footer_meta_html("2026-01-01T00:00:00")
        assert html == "Last updated 2026-01-01T00:00:00"

    def test_escapes_html(self):
        html = build_footer_meta_html("<script>alert(1)</script>")
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
