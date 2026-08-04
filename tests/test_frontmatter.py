"""Tests for frontmatter parsing."""

from __future__ import annotations

from datetime import date

from flydocs.frontmatter import (
    DEFAULT_STATUS,
    VALID_STATUSES,
    VALID_TYPES,
    extract_title,
    get_generated,
    get_stale_after,
    get_status,
    is_human_actor,
    is_stale,
    normalize_tags,
    normalize_verified,
    parse_frontmatter,
    trust_tier,
)


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
        text = '---\ntitle: "Hello: World"\n---\nBody'
        meta, _body = parse_frontmatter(text)
        assert meta["title"] == "Hello: World"

    def test_invalid_yaml_degrades_gracefully(self):
        # An unquoted "key: value: with-colon" line is not valid YAML (a bare
        # colon+space inside a plain scalar is reserved for mapping syntax).
        # Real YAML parsing must not crash on this — it should degrade the
        # same way "no frontmatter found" does.
        text = "---\ntitle: Hello: World\n---\nBody"
        meta, body = parse_frontmatter(text)
        assert meta == {}
        assert body == text

    def test_quoted_value(self):
        text = '---\ntitle: "Quoted Title"\n---\nBody'
        meta, _body = parse_frontmatter(text)
        assert meta["title"] == "Quoted Title"

    def test_empty_body(self):
        text = "---\ntitle: Empty\n---\n"
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "Empty"
        assert body == ""

    def test_no_closing_delimiter(self):
        text = "---\ntitle: Broken\nNo closing delimiter"
        meta, _body = parse_frontmatter(text)
        assert meta == {}

    def test_parses_list_field(self):
        text = "---\ntags: [a, b]\n---\nBody"
        meta, _body = parse_frontmatter(text)
        assert meta["tags"] == ["a", "b"]

    def test_parses_nested_object(self):
        text = "---\ngenerated:\n  by: human:x\n  at: 2026-01-01\n---\nBody"
        meta, _body = parse_frontmatter(text)
        assert meta["generated"]["by"] == "human:x"
        assert meta["generated"]["at"] == date(2026, 1, 1)


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


class TestNormalizeTags:
    def test_missing(self):
        assert normalize_tags({}) == []

    def test_list(self):
        assert normalize_tags({"tags": ["a", "b"]}) == ["a", "b"]

    def test_bare_scalar(self):
        assert normalize_tags({"tags": "solo"}) == ["solo"]


class TestGetStatus:
    def test_default_when_absent(self):
        assert get_status({}) == DEFAULT_STATUS

    def test_explicit_status(self):
        assert get_status({"status": "draft"}) == "draft"

    def test_valid_statuses(self):
        assert VALID_STATUSES == {"draft", "stable", "deprecated"}


class TestGetStaleAfter:
    def test_string_date(self):
        assert get_stale_after({"stale_after": "2026-01-01"}) == date(2026, 1, 1)

    def test_real_date_object(self):
        assert get_stale_after({"stale_after": date(2026, 1, 1)}) == date(2026, 1, 1)

    def test_missing(self):
        assert get_stale_after({}) is None

    def test_malformed(self):
        assert get_stale_after({"stale_after": "not-a-date"}) is None


class TestIsStale:
    def test_no_stale_after(self):
        assert is_stale({}) is False

    def test_past_date_is_stale(self):
        assert is_stale({"stale_after": "2020-01-01"}, today=date(2026, 1, 1)) is True

    def test_today_equals_stale_after_is_stale(self):
        assert is_stale({"stale_after": "2026-01-01"}, today=date(2026, 1, 1)) is True

    def test_future_date_not_stale(self):
        assert is_stale({"stale_after": "2099-01-01"}, today=date(2026, 1, 1)) is False

    def test_malformed_date_not_stale(self):
        assert is_stale({"stale_after": "not-a-date"}) is False


class TestNormalizeVerified:
    def test_missing(self):
        assert normalize_verified({}) == []

    def test_bare_mapping_shorthand(self):
        result = normalize_verified({"verified": {"by": "human:x", "at": "2026-01-01"}})
        assert result == [{"by": "human:x", "at": "2026-01-01"}]

    def test_list(self):
        entries = [
            {"by": "human:x", "at": "2026-01-01"},
            {"by": "process:y", "at": "2026-01-02"},
        ]
        assert normalize_verified({"verified": entries}) == entries

    def test_filters_non_dict_entries(self):
        assert normalize_verified({"verified": ["not-a-dict"]}) == []


class TestIsHumanActor:
    def test_human_prefix(self):
        assert is_human_actor("human:aknochow") is True

    def test_non_human(self):
        assert is_human_actor("reference_agent/gemini-2.5-pro") is False
        assert is_human_actor("process:nightly") is False


class TestTrustTier:
    def test_unverified_when_absent(self):
        assert trust_tier({}) == "unverified"

    def test_machine_confirmed(self):
        meta = {"verified": [{"by": "process:nightly", "at": "2026-01-01"}]}
        assert trust_tier(meta) == "machine-confirmed"

    def test_human_reviewed(self):
        meta = {"verified": [{"by": "human:aknochow", "at": "2026-01-01"}]}
        assert trust_tier(meta) == "human-reviewed"

    def test_human_reviewed_wins_when_mixed(self):
        meta = {
            "verified": [
                {"by": "process:nightly", "at": "2026-01-01"},
                {"by": "human:aknochow", "at": "2026-01-02"},
            ]
        }
        assert trust_tier(meta) == "human-reviewed"


class TestGetGenerated:
    def test_missing(self):
        assert get_generated({}) == {"by": "", "at": ""}

    def test_extracts_by_and_at(self):
        meta = {"generated": {"by": "human:x", "at": "2026-01-01T10:00:00"}}
        result = get_generated(meta)
        assert result["by"] == "human:x"
        assert result["at"] == "2026-01-01T10:00:00"

    def test_date_object_normalized_to_iso_string(self):
        # A bare date (no time component) is assumed midnight UTC.
        meta = {"generated": {"by": "human:x", "at": date(2026, 1, 1)}}
        result = get_generated(meta)
        assert result["at"] == "2026-01-01T00:00:00+00:00"

    def test_malformed_non_dict_returns_empty(self):
        assert get_generated({"generated": "not-a-dict"}) == {"by": "", "at": ""}
