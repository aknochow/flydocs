"""Tests for badge system."""

from __future__ import annotations

from flydocs.badges import (
    _badge_md,
    badges_markdown,
    build_badge_html,
    expand_inline_badges,
)
from flydocs.config import Badge


class TestBadgeMd:
    def test_basic(self):
        b = Badge(id="v", label="v1.0", url="https://x.com", img="https://img.io/v")
        result = _badge_md(b)
        assert "[![v1.0]" in result
        assert "(https://img.io/v)" in result
        assert "(https://x.com)" in result

    def test_escapes_brackets(self):
        b = Badge(id="v", label="v[1.0]", url="https://x.com", img="https://img.io/v")
        result = _badge_md(b)
        assert "\\[" in result
        assert "\\]" in result


class TestBuildBadgeHtml:
    def test_empty(self):
        assert build_badge_html(()) == ""

    def test_renders_html(self, sample_badges):
        html = build_badge_html(sample_badges)
        assert "flydocs-badges" in html
        assert "flydocs-badge" in html
        assert "img.shields.io" in html

    def test_escapes_values(self):
        b = Badge(id="x", label="<script>", url="https://x.com", img="https://img.io/v")
        html = build_badge_html((b,))
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


class TestExpandInlineBadges:
    def test_single_badge(self, sample_badges):
        body = "Version: {{badge:version}}"
        result = expand_inline_badges(body, sample_badges)
        assert "{{badge:" not in result
        assert "v1.0" in result

    def test_all_badges(self, sample_badges):
        body = "All: {{badges}}"
        result = expand_inline_badges(body, sample_badges)
        assert "{{badges}}" not in result
        assert "v1.0" in result
        assert "Docs" in result

    def test_unknown_badge_unchanged(self, sample_badges):
        body = "{{badge:unknown}}"
        result = expand_inline_badges(body, sample_badges)
        assert result == "{{badge:unknown}}"

    def test_empty_badges(self):
        body = "{{badge:version}} and {{badges}}"
        result = expand_inline_badges(body, ())
        assert "{{badge:version}}" in result
        assert "{{badges}}" not in result


class TestBadgesMarkdown:
    def test_generates_markdown(self, sample_badges):
        result = badges_markdown(sample_badges)
        assert "[![v1.0]" in result
        assert "[![Docs]" in result

    def test_empty(self):
        assert badges_markdown(()) == ""
