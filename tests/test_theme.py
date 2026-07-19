"""Tests for theme resolution and rendering."""

from __future__ import annotations

from flydocs.theme import _sanitize_palette, resolve_html_classes


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
