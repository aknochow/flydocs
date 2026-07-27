"""Security tests — XSS, injection, path traversal, input validation."""

from __future__ import annotations

import pytest

from flydocs.badges import build_badge_html, expand_inline_badges
from flydocs.builder import _validate_site_dir
from flydocs.config import Badge, BannerConfig, Config, ThemeConfig
from flydocs.frontmatter import parse_frontmatter
from flydocs.linker import rewrite_links
from flydocs.nav import build_sidebar
from flydocs.theme import _sanitize_palette, build_banner_html, render_page


class TestXssNavSidebar:
    def test_section_title_escaped(self):
        nav = [{"title": '<script>alert("xss")</script>', "entries": []}]
        html = build_sidebar(nav, "other.md")
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_entry_label_escaped(self):
        nav = [
            {
                "title": "T",
                "entries": [{"label": "<img src=x onerror=alert(1)>", "path": "x", "file": "x.md"}],
            }
        ]
        html = build_sidebar(nav, "other.md")
        assert "&lt;img" in html

    def test_entry_href_escaped(self):
        nav = [
            {
                "title": "T",
                "entries": [{"label": "L", "path": '" onclick="alert(1)', "file": "x.md"}],
            }
        ]
        html = build_sidebar(nav, "other.md")
        assert "&quot;" in html
        assert 'href="&quot;' not in html or '" onclick="' not in html


class TestXssBadges:
    def test_badge_label_escaped(self):
        b = Badge(id="x", label="<script>xss</script>", url="https://x", img="https://img.io/x")
        html = build_badge_html((b,))
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_badge_url_escaped(self):
        b = Badge(id="x", label="L", url='" onmouseover="alert(1)', img="https://img.io/x")
        html = build_badge_html((b,))
        assert "&quot;" in html
        assert '" onmouseover="' not in html

    def test_badge_img_escaped(self):
        b = Badge(id="x", label="L", url="https://x", img='" onerror="alert(1)')
        html = build_badge_html((b,))
        assert "&quot;" in html
        assert '" onerror="' not in html


class TestXssBanner:
    def test_banner_text_escaped(self):
        config = Config(theme=ThemeConfig(banner=BannerConfig(text="<script>alert(1)</script>")))
        html = build_banner_html(config)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_banner_url_escaped(self):
        config = Config(
            theme=ThemeConfig(banner=BannerConfig(text="T", url='" onmouseover="alert(1)'))
        )
        html = build_banner_html(config)
        assert "&quot;" in html
        assert '" onmouseover="' not in html

    def test_banner_color_escaped(self):
        config = Config(theme=ThemeConfig(banner=BannerConfig(text="T", color='" class="evil')))
        html = build_banner_html(config)
        assert "&quot;" in html
        assert '" class="evil' not in html


class TestXssTemplate:
    def test_base_path_escaped_in_render(self):
        config = Config(name="T", base_path='"><script>alert(1)</script><x x="')
        html = render_page("<p>X</p>", "T", "", "", "", config)
        assert "<script>alert" not in html
        assert "&lt;script&gt;" in html or "&quot;" in html

    def test_logo_escaped_in_render(self):
        config = Config(name="T", theme=ThemeConfig(logo='" onerror="alert(1)'))
        html = render_page("<p>X</p>", "P", "", "", "", config)
        assert "&quot;" in html
        assert '" onerror="' not in html

    def test_tagline_escaped_in_render(self):
        config = Config(name="T", theme=ThemeConfig(tagline="<img src=x onerror=alert(1)>"))
        html = render_page("<p>X</p>", "P", "", "", "", config)
        assert "&lt;img" in html

    def test_project_name_escaped_in_render(self):
        config = Config(name="<script>alert(1)</script>")
        html = render_page("<p>X</p>", "P", "", "", "", config)
        assert "<script>alert" not in html
        assert "&lt;script&gt;" in html

    def test_description_escaped_in_render(self):
        config = Config(name="T")
        html = render_page("<p>X</p>", "P", "<script>xss</script>", "", "", config)
        assert 'content="&lt;script&gt;' in html


class TestXssLinker:
    def test_base_path_escaped_in_rewrite(self):
        html = '<a href="other.md">Link</a>'
        result = rewrite_links(html, "index.md", base_path='"><script>')
        assert "<script>" not in result
        assert "&quot;" in result or "&lt;" in result


class TestPaletteValidation:
    def test_rejects_injection(self):
        assert _sanitize_palette('" onload="alert(1)') == "default"

    def test_rejects_spaces(self):
        assert _sanitize_palette("my palette") == "default"

    def test_rejects_html(self):
        assert _sanitize_palette("<script>") == "default"

    def test_rejects_uppercase(self):
        assert _sanitize_palette("MyPalette") == "default"

    def test_allows_valid(self):
        assert _sanitize_palette("custom-dark-v2") == "custom-dark-v2"

    def test_allows_numbers(self):
        assert _sanitize_palette("theme42") == "theme42"


class TestPathTraversal:
    def test_site_dir_escaping_blocked(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(SystemExit, match="escapes project root"):
            _validate_site_dir("/etc")

    def test_site_dir_parent_traversal_blocked(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(SystemExit, match="escapes project root"):
            _validate_site_dir("../../escape")

    def test_site_dir_absolute_blocked(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(SystemExit, match="escapes project root"):
            _validate_site_dir("/tmp/evil")

    def test_site_dir_relative_allowed(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _validate_site_dir("public")

    def test_site_dir_nested_relative_allowed(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _validate_site_dir("build/output")


class TestFrontmatterInjection:
    def test_dashes_in_value_dont_break_parser(self):
        text = "---\ntitle: A --- B --- C\n---\nBody"
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "A --- B --- C"
        assert body == "Body"

    def test_yaml_anchor_not_executed(self):
        text = "---\ntitle: *anchor\nref: &anchor value\n---\nBody"
        meta, body = parse_frontmatter(text)
        assert "anchor" in meta.get("title", "")
        assert body == "Body"

    def test_indented_lines_parsed_as_keys(self):
        text = "---\ntitle: line1\n  extra_key: extra_value\n---\nBody"
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "line1"
        assert body == "Body"


class TestInlineBadgeInjection:
    def test_badge_id_regex_rejects_special_chars(self):
        body = "{{badge:<script>}}"
        result = expand_inline_badges(body, ())
        assert result == body

    def test_badge_id_regex_rejects_spaces(self):
        body = "{{badge:my badge}}"
        result = expand_inline_badges(body, ())
        assert result == body

    def test_badge_id_regex_rejects_slashes(self):
        body = "{{badge:../../etc/passwd}}"
        result = expand_inline_badges(body, ())
        assert result == body
