"""Parse OKF frontmatter from markdown files."""

from __future__ import annotations

import re


VALID_TYPES = {"Concept", "Guide", "Reference", "Example"}

_FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse YAML frontmatter from a markdown document.

    Returns (metadata_dict, body_text). If no frontmatter is found,
    returns an empty dict and the full text.
    """
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    fm_text = m.group(1).strip()
    body = m.group(2).strip()
    meta: dict[str, str] = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, body


def extract_title(meta: dict[str, str], body: str, fallback: str = "Documentation") -> str:
    """Extract page title from frontmatter or first heading."""
    if "title" in meta:
        return meta["title"]
    match = re.match(r"^#\s+(.+)", body, re.MULTILINE)
    if match:
        return match.group(1)
    return fallback
