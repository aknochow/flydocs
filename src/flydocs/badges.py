"""Badge loading, HTML generation, and inline markdown expansion."""

from __future__ import annotations

import html as html_module
import re

from flydocs.config import Badge


def _badge_md(badge: Badge) -> str:
    """Convert a badge to markdown image-link syntax."""
    label = badge.label.replace("[", "\\[").replace("]", "\\]")
    img = badge.img.replace("(", "\\(").replace(")", "\\)")
    url = badge.url.replace("(", "\\(").replace(")", "\\)")
    return f"[![{label}]({img})]({url})"


def build_badge_html(badges: list[Badge] | tuple[Badge, ...]) -> str:
    """Generate HTML for the badge bar in the site header."""
    if not badges:
        return ""
    html = '<span class="flydocs-badges">'
    for b in badges:
        if not (b.label and b.img and b.url):
            continue
        html += (
            f'<a href="{html_module.escape(b.url)}" class="flydocs-badge" '
            f'target="_blank" rel="noopener noreferrer" '
            f'aria-label="{html_module.escape(b.label)}">'
            f'<img src="{html_module.escape(b.img)}" '
            f'alt="{html_module.escape(b.label)}"></a>'
        )
    html += "</span>"
    return html


def expand_inline_badges(body: str, badges: list[Badge] | tuple[Badge, ...]) -> str:
    """Expand {{badge:id}} and {{badges}} in markdown before processing.

    {{badge:version}} expands to a single badge as a markdown image-link.
    {{badges}} expands to the full badge bar as markdown.
    """
    badge_map = {b.id: b for b in badges if b.id}

    def replace_single(m: re.Match) -> str:
        badge = badge_map.get(m.group(1))
        if not badge:
            return m.group(0)
        return _badge_md(badge)

    body = re.sub(r"\{\{badge:([\w][\w-]*)\}\}", replace_single, body)

    if "{{badges}}" in body:
        parts = [_badge_md(b) for b in badges if b.label and b.img and b.url]
        body = body.replace("{{badges}}", " ".join(parts))

    return body


def badges_markdown(badges: list[Badge] | tuple[Badge, ...]) -> str:
    """Generate copy-pasteable badge markdown for README files."""
    parts = [_badge_md(b) for b in badges if b.label and b.img and b.url]
    return " ".join(parts)
