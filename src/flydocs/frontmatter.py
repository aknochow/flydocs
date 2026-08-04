"""Parse OKF frontmatter from markdown files."""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Any

import yaml

VALID_TYPES = {"Concept", "Guide", "Reference", "Example"}
VALID_STATUSES = {"draft", "stable", "deprecated"}
DEFAULT_STATUS = "stable"

_FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from a markdown document.

    Returns (metadata_dict, body_text). If no frontmatter is found, or the
    frontmatter block is not valid YAML, returns an empty dict and the full
    text unchanged.
    """
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    fm_text = m.group(1).strip()
    body = m.group(2).strip()
    try:
        meta = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return {}, text
    if not isinstance(meta, dict):
        return {}, text
    return meta, body


def extract_title(meta: dict[str, Any], body: str, fallback: str = "Documentation") -> str:
    """Extract page title from frontmatter or first heading."""
    if "title" in meta:
        return str(meta["title"])
    match = re.match(r"^#\s+(.+)", body, re.MULTILINE)
    if match:
        return match.group(1)
    return fallback


def normalize_tags(meta: dict[str, Any]) -> list[str]:
    """Return the 'tags' field as a list of strings, regardless of source shape."""
    tags = meta.get("tags")
    if tags is None:
        return []
    if isinstance(tags, list):
        return [str(t) for t in tags]
    return [str(tags)]


def get_status(meta: dict[str, Any]) -> str:
    """Return the OKF 'status' field, defaulting to 'stable' when absent."""
    status = meta.get("status")
    if status is None:
        return DEFAULT_STATUS
    return str(status)


def _coerce_to_date(value: Any) -> date | None:
    """Tolerantly coerce a YAML-parsed value into a date."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def _coerce_to_datetime(value: Any) -> datetime | None:
    """Tolerantly coerce a YAML-parsed value into a datetime.

    A bare date (no time component) is assumed to be midnight UTC, matching
    the OKF spec's use of 'Z'-suffixed (UTC) example timestamps.
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.strip())
        except ValueError:
            d = _coerce_to_date(value)
            return datetime(d.year, d.month, d.day, tzinfo=timezone.utc) if d else None
    return None


def get_stale_after(meta: dict[str, Any]) -> date | None:
    """Return the OKF 'stale_after' field as a date, or None if absent/unparseable."""
    return _coerce_to_date(meta.get("stale_after"))


def is_stale(meta: dict[str, Any], today: date | None = None) -> bool:
    """Return True if 'stale_after' is set and has passed."""
    stale_after = get_stale_after(meta)
    if stale_after is None:
        return False
    today = today or datetime.now(timezone.utc).date()
    return today >= stale_after


def normalize_verified(meta: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the OKF 'verified' field as a list of {by, at} dicts.

    A bare single mapping is treated as a one-element list, per spec.
    """
    verified = meta.get("verified")
    if verified is None:
        return []
    if isinstance(verified, dict):
        return [verified]
    if isinstance(verified, list):
        return [v for v in verified if isinstance(v, dict)]
    return []


def is_human_actor(actor: str) -> bool:
    """Return True if the actor string uses the 'human:<id>' convention."""
    return isinstance(actor, str) and actor.startswith("human:")


def trust_tier(meta: dict[str, Any]) -> str:
    """Derive a trust tier from 'verified': unverified, machine-confirmed, or human-reviewed."""
    entries = normalize_verified(meta)
    if not entries:
        return "unverified"
    if any(is_human_actor(e.get("by", "")) for e in entries):
        return "human-reviewed"
    return "machine-confirmed"


def get_generated(meta: dict[str, Any]) -> dict[str, str]:
    """Return the OKF 'generated' field as {'by': str, 'at': str}, defaulting to ''."""
    generated = meta.get("generated")
    if not isinstance(generated, dict):
        return {"by": "", "at": ""}
    by = generated.get("by") or ""
    at_dt = _coerce_to_datetime(generated.get("at"))
    at = at_dt.isoformat() if at_dt else ""
    return {"by": str(by), "at": at}
