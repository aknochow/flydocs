"""Tests for URL slug generation and link rewriting."""

from __future__ import annotations

import pytest

from flydocs.linker import md_to_slug, rewrite_links, slug_to_href


class TestMdToSlug:
    def test_index(self):
        assert md_to_slug("index.md") == ""

    def test_nested_index(self):
        assert md_to_slug("concepts/index.md") == "concepts"

    def test_regular_file(self):
        assert md_to_slug("concepts/gateway.md") == "concepts/gateway"

    def test_top_level_file(self):
        assert md_to_slug("quickstart.md") == "quickstart"

    def test_deep_nesting(self):
        assert md_to_slug("a/b/c/page.md") == "a/b/c/page"

    def test_non_md_raises(self):
        with pytest.raises(ValueError, match="Expected .md path"):
            md_to_slug("readme.txt")

    def test_windows_paths(self):
        assert md_to_slug("concepts\\gateway.md") == "concepts/gateway"


class TestSlugToHref:
    def test_empty_slug(self):
        assert slug_to_href("") == "/"

    def test_with_slug(self):
        assert slug_to_href("concepts/gateway") == "/concepts/gateway/"

    def test_with_base_path(self):
        assert slug_to_href("concepts/gateway", "/docs") == "/docs/concepts/gateway/"

    def test_empty_slug_with_base(self):
        assert slug_to_href("", "/docs") == "/docs/"


class TestRewriteLinks:
    def test_basic_rewrite(self):
        html = '<a href="other.md">Link</a>'
        result = rewrite_links(html, "index.md")
        assert 'href="/other/"' in result

    def test_relative_link(self):
        html = '<a href="../index.md">Home</a>'
        result = rewrite_links(html, "guides/quickstart.md")
        assert 'href="/"' in result

    def test_fragment_preserved(self):
        html = '<a href="config.md#theme">Theme</a>'
        result = rewrite_links(html, "index.md")
        assert "#theme" in result

    def test_external_links_untouched(self):
        html = '<a href="https://example.com">External</a>'
        result = rewrite_links(html, "index.md")
        assert 'href="https://example.com"' in result

    def test_with_base_path(self):
        html = '<a href="other.md">Link</a>'
        result = rewrite_links(html, "index.md", base_path="/flydocs")
        assert 'href="/flydocs/other/"' in result
