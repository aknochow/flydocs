"""Frontmatter, navigation, and link validation."""

from __future__ import annotations

import os
import posixpath
import re
from datetime import date, datetime, timezone
from typing import Any

from flydocs.builder import collect_md_files
from flydocs.config import Config
from flydocs.frontmatter import (
    VALID_STATUSES,
    VALID_TYPES,
    get_stale_after,
    is_stale,
    normalize_verified,
    parse_frontmatter,
)


def _lint_okf_v2(md_rel: str, meta: dict[str, Any], today: date, warnings: list[str]) -> None:
    """Check OKF v0.2 fields (status, stale_after, generated, verified, sources).

    All checks here are warnings, never errors: per the OKF spec, the only
    hard requirement anywhere is a non-empty 'type' field.
    """
    status = meta.get("status")
    if status is not None and status not in VALID_STATUSES:
        warnings.append(f"{md_rel}: status '{status}' not in {VALID_STATUSES}")

    stale_after_raw = meta.get("stale_after")
    if stale_after_raw is not None:
        if get_stale_after(meta) is None:
            warnings.append(f"{md_rel}: stale_after '{stale_after_raw}' is not a valid date")
        elif is_stale(meta, today):
            warnings.append(f"{md_rel}: stale (stale_after: {stale_after_raw})")

    generated = meta.get("generated")
    if isinstance(generated, dict) and not generated.get("by"):
        warnings.append(f"{md_rel}: generated block missing 'by'")

    for entry in normalize_verified(meta):
        if not entry.get("by"):
            warnings.append(f"{md_rel}: verified entry missing 'by'")

    sources = meta.get("sources")
    if isinstance(sources, list):
        for entry in sources:
            if not isinstance(entry, dict) or not entry.get("resource"):
                warnings.append(f"{md_rel}: sources entry missing 'resource'")


def lint(config: Config, strict: bool = False, today: date | None = None) -> int:
    """Validate all docs against OKF and config rules. Returns exit code."""
    errors: list[str] = []
    warnings: list[str] = []
    today = today or datetime.now(timezone.utc).date()

    nav_files: set[str] = set()
    for section in config.nav:
        for items in section.values():
            for item in items:
                for path in item.values():
                    nav_files.add(path)

    md_files = collect_md_files(config.docs_dir)

    for md_rel in md_files:
        with open(os.path.join(config.docs_dir, md_rel)) as f:
            raw = f.read()

        meta, body = parse_frontmatter(raw)

        if not meta:
            errors.append(f"{md_rel}: missing frontmatter")
            continue

        if not meta.get("type"):
            errors.append(f"{md_rel}: missing required field 'type'")
        elif meta["type"] not in VALID_TYPES:
            warnings.append(f"{md_rel}: type '{meta['type']}' not in {VALID_TYPES}")

        for field in ("title", "description"):
            if not meta.get(field):
                errors.append(f"{md_rel}: missing field '{field}'")

        _lint_okf_v2(md_rel, meta, today, warnings)

        if config.nav and md_rel not in nav_files:
            warnings.append(f"{md_rel}: not in nav")

        current_dir = posixpath.dirname(md_rel)
        for match in re.finditer(r"\[([^\]]+)\]\(([^)#]+)\.md(?:#[^)]*)?\)", body):
            href = match.group(2)
            if href.startswith("http"):
                continue
            if current_dir:
                resolved = posixpath.normpath(posixpath.join(current_dir, href))
            else:
                resolved = posixpath.normpath(href)
            resolved = resolved.lstrip("/") + ".md"
            if not os.path.exists(os.path.join(config.docs_dir, resolved)):
                errors.append(f"{md_rel}: broken link to '{resolved}'")

    for nav_file in nav_files:
        if not os.path.exists(os.path.join(config.docs_dir, nav_file)):
            errors.append(f"nav: '{nav_file}' listed but file missing")

    if warnings:
        for w in warnings:
            print(f"  WARN  {w}")
    if errors:
        for e in errors:
            print(f"  FAIL  {e}")
        print(f"\nLint failed: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1

    if strict and warnings:
        print(f"\nLint failed (strict): {len(warnings)} warning(s)")
        return 1

    print(f"Lint passed: {len(md_files)} docs checked, {len(warnings)} warning(s)")
    return 0
