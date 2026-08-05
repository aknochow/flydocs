---
type: Guide
title: OKF Compliance Guide
description: Step-by-step guide to building an OKF-compliant doc set, from scratch or from an existing docs directory.
tags: [okf, compliance, migration, guide, agent-guide]
status: stable
generated:
  by: human:aknochow
  at: 2026-08-05T00:00:00Z
---

# OKF Compliance Guide

[TOC]

This is the practical companion to [OKF Frontmatter Standard](okf.md) —
that page is the field reference (what each field means); this page is
the process (how to actually get a doc set compliant), for two starting
points: a project with no docs yet, and a project with docs that
predate OKF.

Compliance means `flydocs lint` reports zero warnings. That's the bar
this repo's own `docs/` holds itself to — every field described here is
in real use in this directory.

## Quick Compliance Checklist

| Field | Required? | Notes |
|-------|-----------|-------|
| `type` | **Required** | One of `Concept`, `Guide`, `Reference`, `Example` — see [Choosing a Type](okf.md#choosing-a-type). |
| `title` | **Required** | Page title. |
| `description` | **Required** | One-line summary. |
| `tags` | Optional | Search/grouping keywords. |
| `weight` | Optional | Nav sort order. |
| `status` | Recommended | `draft` / `stable` / `deprecated`. Omit only if you have no opinion on lifecycle state — it defaults to `stable`. |
| `generated` | Recommended | `{by, at}` — who/what wrote this doc and when. Set truthfully: if an agent wrote it, `by` should say so, not claim `human:` authorship. |
| `verified` | Situational | Only if a human or process has actually confirmed the content against sources — don't add it speculatively. |
| `sources` | Situational | Only if the doc was derived from specific files/URLs worth citing. |
| `stale_after` | Situational | Only if the content has a real expiration (e.g. tied to a version, a contract, a scheduled review). |

The last three are "situational," not optional-as-in-skippable-by-default
— add them when they're true, omit them when they're not. Fabricating
a `verified` entry that never happened is worse than leaving the field
off.

## Starting a New Project

Write every doc directly in compliant form. Do not write plain
markdown first and convert it afterward — that touches every doc
twice for no benefit, since the type/description/provenance decisions
are easiest to make at the moment you're already writing the content.

1. For each doc, start with the required three fields:

   ```yaml
   ---
   type: Guide
   title: Page Title
   description: One-line summary, used in search and previews.
   ---
   ```

2. Add `status` and `generated` while you write, not after:

   ```yaml
   status: stable          # or draft, if genuinely incomplete
   generated:
     by: human:yourname     # or claude-code/sonnet-5, or process:ci-nightly
     at: 2026-08-05T00:00:00Z
   ```

   See [Actor convention](okf.md#v02-status-staleness-and-provenance)
   for the `by` format — set it to whichever actor is actually doing
   the writing. An agent authoring a doc should not claim `human:`
   authorship it didn't have.

3. Run `flydocs lint` before considering any doc done. Zero warnings,
   every time — don't let warnings accumulate across a batch of new docs.

Read this repo's own `docs/*.md` frontmatter blocks for a live,
lint-passing example of all of the above in real use — they're not
just an illustration, they're the actual compliance bar.

## Auditing and Converting Existing Docs

For a docs directory that predates OKF, work file by file rather than
trying to batch-classify everything up front — type and provenance
decisions are easiest to make with one file's actual content in front
of you.

1. **Inventory.** List every `.md` file under `docs_dir`. `flydocs
   lint` will do this for you and report every file missing
   frontmatter entirely as `missing frontmatter` — that's your
   worklist.

2. **Classify each file's type**, using [Choosing a Type](okf.md#choosing-a-type):
   learning → `Concept`, doing → `Guide`, looking up → `Reference`,
   copying → `Example`. If a file doesn't cleanly fit one type, that's
   often a sign it should be split, not a sign the type system is
   wrong for it.

3. **Add the three required fields** (`type`, `title`, `description`)
   to each file's frontmatter block. `title` can usually come from the
   file's first `# heading`; `description` needs an actual one-line
   summary — don't leave it as a placeholder.

4. **Decide `status` per file**, honestly: is this doc actually
   current (`stable`), known to be incomplete or unreviewed (`draft`),
   or kept only for link continuity (`deprecated`)?

5. **Add `generated`/`verified` only where you know the real answer.**
   For docs with an unclear or lost authorship history, it's fine to
   omit `generated` entirely rather than guess — an absent field is
   honest; a fabricated one is not. If a re-review happens as part of
   this migration, that's a legitimate `verified` entry to add
   (`by: human:<you>`, `at: <today>`).

6. **Run `flydocs lint`, fix warnings, repeat** until it reports zero
   warnings. Use the lookup table below to interpret each warning.

## Fixing `flydocs lint` Warnings

| Warning | What it means | Fix |
|---------|---------------|-----|
| `missing frontmatter` | No `---` block at all, or the block failed to parse as YAML (check the flydocs build log for a matching `Invalid YAML frontmatter` message) | Add a frontmatter block; if one exists but isn't being read, check for invalid YAML (e.g. an unquoted value containing `: `) |
| `missing required field 'type'` | No `type:` key | Add `type:`, one of the four OKF types |
| `type 'X' not in {...}` | `type` is set but isn't one of the four valid values | Fix the value — check for a typo or an invented type |
| `missing field 'title'` / `missing field 'description'` | Field absent or empty | Add real content, not a placeholder |
| `not in nav` | File exists but isn't referenced in `flydocs.toml`'s `[[nav]]` | Add an entry, or omit `[[nav]]` entirely to use directory-based navigation |
| `broken link to 'X'` | A relative markdown link points at a file that doesn't exist | Fix the path, or remove the link |
| `status 'X' not in {...}` | `status` is set but isn't `draft`/`stable`/`deprecated` | Fix the value |
| `stale_after 'X' is not a valid date` | Value isn't `YYYY-MM-DD` | Fix the format |
| `stale (stale_after: X)` | The doc's own declared expiration has passed | Review the content, then either update it and bump `stale_after`, or leave it and accept the warning as an honest signal |
| `generated block missing 'by'` | `generated` is present but has no `by` | Add `by` (actor convention), or remove the `generated` block if you don't actually know |
| `verified entry missing 'by'` | A `verified` entry has no `by` | Add `by` to that entry |
| `sources entry missing 'resource'` | A `sources` entry has no `resource` | Add the path/URL, or remove the incomplete entry |

All of the OKF v0.2 checks above (`status`, `stale_after`, `generated`,
`verified`, `sources`) are warnings, never hard failures — that
matches the OKF spec's own conformance rule that only a non-empty
`type` is ever required. `flydocs` itself enforces a few additional
hard requirements beyond that spec minimum: missing `title`/
`description`, a broken relative link, and a `[[nav]]` entry pointing
at a file that doesn't exist all exit non-zero too. Run with
`--strict` to fail the build on any warning as well, once you're
aiming for the zero-warning bar.

## Planned Tooling

`flydocs okf preview` and `flydocs okf init` are **not yet
implemented** — both currently exit with an error. Once available,
they'll automate parts of the audit above (inferring types, scaffolding
frontmatter). Until then, this guide's manual process is the actual
path to compliance.

## See Also

- [OKF Frontmatter Standard](okf.md) — full field reference, actor
  convention, trust tiers, and the relationship to Google's OKF v0.2 spec.
