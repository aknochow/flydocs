"""Tests for frontmatter parsing."""

from __future__ import annotations

from flydocs.frontmatter import VALID_TYPES, extract_title, parse_frontmatter


class TestParseFrontmatter:
    def test_basic_frontmatter(self):
        text = "---\ntype: Guide\ntitle: Hello\n---\nBody here."
        meta, body = parse_frontmatter(text)
        assert meta["type"] == "Guide"
        assert meta["title"] == "Hello"
        assert body == "Body here."

    def test_no_frontmatter(self):
        text = "Just a plain document."
        meta, body = parse_frontmatter(text)
        assert meta == {}
        assert body == "Just a plain document."

    def test_dashes_in_values(self):
        text = "---\ntitle: My --- Title\ndescription: Has --- dashes\n---\nBody"
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "My --- Title"
        assert body == "Body"

    def test_colon_in_value(self):
        text = "---\ntitle: Hello: World\n---\nBody"
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "Hello: World"

    def test_quoted_value(self):
        text = '---\ntitle: "Quoted Title"\n---\nBody'
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "Quoted Title"

    def test_empty_body(self):
        text = "---\ntitle: Empty\n---\n"
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "Empty"
        assert body == ""

    def test_no_closing_delimiter(self):
        text = "---\ntitle: Broken\nNo closing delimiter"
        meta, body = parse_frontmatter(text)
        assert meta == {}


class TestExtractTitle:
    def test_from_meta(self):
        assert extract_title({"title": "Meta Title"}, "# Heading") == "Meta Title"

    def test_from_heading(self):
        assert extract_title({}, "# First Heading\nContent") == "First Heading"

    def test_fallback(self):
        assert extract_title({}, "No heading here") == "Documentation"

    def test_custom_fallback(self):
        assert extract_title({}, "No heading", fallback="Custom") == "Custom"


class TestValidTypes:
    def test_expected_types(self):
        assert VALID_TYPES == {"Concept", "Guide", "Reference", "Example"}
