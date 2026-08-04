"""CLI-side documentation search against frontmatter metadata."""

from __future__ import annotations

import os
from typing import Any

from flydocs.builder import collect_md_files
from flydocs.config import Config
from flydocs.frontmatter import normalize_tags, parse_frontmatter


def search(query: str, config: Config) -> None:
    """Search docs by title, description, and tags."""
    query_lower = query.lower()
    results: list[tuple[int, str, dict[str, Any]]] = []

    for md_rel in collect_md_files(config.docs_dir):
        with open(os.path.join(config.docs_dir, md_rel)) as f:
            raw = f.read()

        meta, _ = parse_frontmatter(raw)
        if not meta:
            continue

        title = meta.get("title", "")
        description = meta.get("description", "")
        tags_str = ", ".join(normalize_tags(meta))
        score = 0

        if query_lower in title.lower():
            score += 3
        if query_lower in description.lower():
            score += 2
        if query_lower in tags_str.lower():
            score += 1

        if score > 0:
            results.append((score, md_rel, meta))

    results.sort(key=lambda x: -x[0])

    if not results:
        print(f"No docs matching '{query}'")
        return

    print(f"Found {len(results)} doc(s) matching '{query}':\n")
    for _score, md_rel, meta in results:
        doc_type = meta.get("type", "?")
        title = meta.get("title", md_rel)
        desc = meta.get("description", "")
        tags_str = ", ".join(normalize_tags(meta))
        print(f"  [{doc_type}] {title}")
        print(f"    {desc}")
        print(f"    tags: {tags_str}")
        print(f"    path: {config.docs_dir}/{md_rel}")
        print()
