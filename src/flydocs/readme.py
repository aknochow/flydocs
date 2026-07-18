"""Generate README.md from docs/index.md."""

from __future__ import annotations

import os
import re

from flydocs.badges import badges_markdown, expand_inline_badges
from flydocs.config import Config
from flydocs.frontmatter import parse_frontmatter


def generate_readme(config: Config) -> str:
    """Generate README content from docs/index.md.

    Strips OKF frontmatter, prepends badge bar, expands inline badges,
    and rewrites docs-relative links to point at the docs site URL.
    """
    index_path = os.path.join(config.docs_dir, "index.md")
    if not os.path.exists(index_path):
        raise SystemExit(f"Error: {index_path} not found")

    with open(index_path) as f:
        raw = f.read()

    _meta, body = parse_frontmatter(raw)

    body = expand_inline_badges(body, config.badges)

    if config.url:
        body = _rewrite_doc_links(body, config.url)

    badge_line = badges_markdown(config.badges)

    parts = []
    if badge_line:
        parts.append(badge_line)
        parts.append("")
    parts.append(body)
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append(f"*Generated from `{config.docs_dir}/index.md` by "
                 f"[flydocs](https://github.com/aknochow/flydocs).*")
    parts.append("")

    return "\n".join(parts)


def _rewrite_doc_links(body: str, site_url: str) -> str:
    """Rewrite relative .md links to point at the docs site."""
    base = site_url.rstrip("/")

    def replace(m: re.Match) -> str:
        text = m.group(1)
        path = m.group(2)
        frag = m.group(3) or ""
        parts = path.replace(".md", "").split("/")
        if parts[-1] == "index":
            parts = parts[:-1]
        slug = "/".join(parts).strip("/")
        if slug:
            return f"[{text}]({base}/{slug}/{frag})"
        return f"[{text}]({base}/{frag})"

    return re.sub(r"\[([^\]]+)\]\(([^)#:]+)\.md(#[^)]*)?\)", replace, body)
