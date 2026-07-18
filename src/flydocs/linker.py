"""URL slug generation and markdown link rewriting."""

from __future__ import annotations

import html as html_module
import posixpath
import re


def md_to_slug(md_rel: str) -> str:
    """Convert a docs-relative .md path to its URL slug.

    Examples:
        index.md            -> ""
        concepts/index.md   -> "concepts"
        concepts/gateway.md -> "concepts/gateway"
    """
    parts = md_rel.replace("\\", "/").split("/")
    if parts[-1] == "index.md":
        parts = parts[:-1]
    elif parts[-1].endswith(".md"):
        parts[-1] = parts[-1][:-3]
    else:
        raise ValueError(f"Expected .md path, got: {md_rel!r}")
    return "/".join(parts)


def slug_to_href(slug: str, base_path: str = "") -> str:
    """Convert a slug to its full site href."""
    if not slug:
        return f"{base_path}/"
    return f"{base_path}/{slug}/"


def rewrite_links(html: str, md_rel: str, base_path: str = "") -> str:
    """Rewrite .md hrefs in HTML to absolute site paths."""
    current_dir = posixpath.dirname(md_rel.replace("\\", "/"))

    def replace(m: re.Match) -> str:
        href = m.group(1)
        frag = m.group(2) or ""
        if current_dir:
            resolved = posixpath.normpath(posixpath.join(current_dir, href))
        else:
            resolved = posixpath.normpath(href)
        resolved = resolved.lstrip("/")
        resolved_md = resolved + ".md"
        slug = md_to_slug(resolved_md)
        return f'href="{html_module.escape(slug_to_href(slug, base_path))}{frag}"'

    return re.sub(r'href="([^"#:]+)\.md(#[^"]*)?"', replace, html)
