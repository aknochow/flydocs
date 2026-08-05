---
type: Reference
title: OKF Frontmatter Standard
description: The Open Knowledge Format used by flydocs for structured documentation.
tags: [okf, frontmatter, standard, metadata]
status: stable
generated:
  by: human:aknochow
  at: 2026-08-03T00:00:00Z
---

# OKF Frontmatter Standard

[TOC]

OKF (Open Knowledge Format) is a YAML frontmatter convention for markdown
documentation. It enables auto-generated navigation, search indexing,
linting, and type-based styling in flydocs sites.

OKF is **optional**. FlyDocs builds PatternFly documentation sites from
plain markdown with no frontmatter required. OKF adds structure when
you want it.

## Frontmatter Block

Every OKF document starts with a YAML block delimited by `---`:

```yaml
---
type: Guide
title: Getting Started
description: Install and run your first build in under 5 minutes.
tags: [quickstart, install]
---
```

## Fields

### Required

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Document category. One of the four OKF types below. |
| `title` | string | Page title. Used in browser tab, nav, and search results. |
| `description` | string | One-line summary. Used in HTML meta, search index, and previews. |

### Optional

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `tags` | list | `[]` | Keywords for search filtering and grouping. |
| `weight` | integer | `0` | Sort order within a nav section. Lower values appear first. |

Projects may add custom fields beyond these five. FlyDocs ignores
fields it does not recognize.

### v0.2 — Status, Staleness, and Provenance

These five fields are optional and align field-for-field with
[Google's OKF v0.2 specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
(see [Relationship to Google OKF](#relationship-to-google-okf) below).

| Field | Type | Description |
|-------|------|-------------|
| `status` | enum | `draft`, `stable`, or `deprecated`. Defaults to `stable` when absent. |
| `stale_after` | date (`YYYY-MM-DD`) | Absolute cutoff. The doc is considered stale once `today >= stale_after`. |
| `generated` | object | `{by, at}` — records automated authorship. `by` is required if `generated` is present. |
| `verified` | object or list | One or more `{by, at}` confirmation events. A single mapping is shorthand for a one-element list. |
| `sources` | list | Objects with a required `resource` (path/URL/scope descriptor), plus optional `id`, `title`, `author`, `usage_count`, `last_modified`. |

**Actor convention** — used by `generated.by`, `verified[].by`, and
`sources[].author`:

- `<producer>/<version>` for agents and tools, e.g. `reference_agent/gemini-2.5-pro`
- `human:<id>` for a person, e.g. `human:aknochow`
- `process:<id>` for an automated process, e.g. `process:nightly-build`

**Trust tier** — consumers derive a trust tier from `verified`:

- No `verified` key → **unverified**
- `verified` entries all by non-`human:` actors → **machine-confirmed**
- Any `verified` entry by a `human:<id>` actor → **human-reviewed**

Example combining all five fields:

```yaml
---
type: Reference
title: Revenue Configuration
description: How revenue figures are computed and reported.
status: stable
generated:
  by: reference_agent/gemini-2.5-pro
  at: 2026-07-01T09:00:00Z
verified:
  - by: human:aknochow
    at: 2026-07-02
stale_after: 2026-12-01
sources:
  - resource: src/billing/revenue.py
    title: Revenue calculation module
    last_modified: 2026-06-28
---
```

A `status: draft` or `status: deprecated` doc shows a label on the built
page; a `deprecated` doc also shows a deprecation notice, and a doc past
its `stale_after` date shows a staleness warning. A doc with `generated.at`
set shows a "Last updated" line in the footer.

## Document Types

OKF defines four content types. Every document belongs to exactly one.

### Concept

Explains **what** something is and **why** it exists. Covers architecture,
design decisions, and mental models. Does not include step-by-step
instructions.

```yaml
type: Concept
title: Gateway Architecture
description: How the gateway manages routing, TLS, and authentication.
```

Examples: architecture overviews, security models, design rationale.

### Guide

Explains **how** to do something. Step-by-step instructions with a clear
goal. Includes tutorials, how-tos, quickstarts, and operational runbooks.

```yaml
type: Guide
title: Quickstart
description: Deploy the operator and create your first instance in 10 minutes.
```

Examples: installation guides, migration procedures, troubleshooting
walkthroughs, upgrade runbooks.

### Reference

Documents **facts**: APIs, CLI flags, configuration keys, environment
variables, CRD specs, or any structured data a user looks up rather
than reads top-to-bottom.

```yaml
type: Reference
title: Configuration
description: All configuration keys, types, defaults, and examples.
```

Examples: API references, CLI usage, config file documentation, CRD
field tables, environment variable listings.

### Example

Shows a **complete, working scenario**. Combines concepts and steps into
a self-contained recipe that a user can copy and adapt.

```yaml
type: Example
title: Claude Code with Vertex AI
description: Run Claude Code in sandboxes using Google Vertex AI as the provider.
```

Examples: integration recipes, sample configurations, worked use cases.

## Choosing a Type

| I want to explain... | Type |
|----------------------|------|
| What something is or why it works this way | Concept |
| How to accomplish a specific task | Guide |
| The exact options, fields, or API surface | Reference |
| A complete working scenario to copy | Example |

When in doubt: if the reader is **learning**, it is a Concept. If the
reader is **doing**, it is a Guide. If the reader is **looking up**, it
is a Reference. If the reader is **copying**, it is an Example.

## Directory Convention

OKF documents **may** be organized by type:

```
docs/
  concepts/
  guides/
  reference/
  examples/
```

This is a convention, not a requirement. FlyDocs reads the `type` field
from frontmatter regardless of file location. A flat `docs/` directory
with explicit `type` fields works the same way.

When both are present, the frontmatter `type` field is authoritative.
A file at `docs/guides/setup.md` with `type: Reference` is a Reference.

## FlyDocs Without OKF

FlyDocs does not require OKF frontmatter. Plain markdown files produce
a PatternFly documentation site with:

- Navigation derived from file and directory names
- Page titles extracted from the first `# heading`
- No search index or type-based styling

This is the default for projects that already have markdown docs and
want a PatternFly site without restructuring their content.

## Migrating to OKF

For the actual step-by-step process — starting a new project's docs or
auditing an existing set to compliance, plus a lookup table for every
`flydocs lint` warning — see the [OKF Compliance Guide](okf-compliance-guide.md).

FlyDocs plans tooling to automate parts of that process:

### Preview *(planned, not yet implemented)*

```bash
flydocs okf preview
```

Intended to infer types from directory names and headings, generate
suggested frontmatter, and build a preview site at `public-okf/`
without touching source files. Currently exits with an error.

### Init *(planned, not yet implemented)*

```bash
flydocs okf init docs/
```

Intended to scaffold a suggested `---` block onto `.md` files that
have no frontmatter, based on filename, directory, and first heading.
Currently exits with an error.

### Lint

Validate OKF frontmatter across all docs:

```bash
flydocs lint
```

Reports missing required fields, unknown types, empty descriptions,
and orphan pages not in the nav. Also warns (never fails, per the OKF
conformance rules) on: an invalid `status` value, an unparseable or
past `stale_after` date, a `generated` block missing `by`, a `verified`
entry missing `by`, or a `sources` entry missing `resource`.

## Relationship to Google OKF

Google's [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)
is a vendor-neutral format for representing knowledge as markdown
files with YAML frontmatter. Google's reference implementation is a
BigQuery metadata catalog tool — it extracts dataset schemas into
OKF-formatted markdown using a Python agent and Gemini enrichment.

FlyDocs adopts the **format concept** from Google's OKF — markdown
files with a `---` YAML frontmatter block containing a `type` field —
but uses its own documentation-oriented type system:

| Google OKF types | FlyDocs OKF types |
|-----------------|-------------------|
| datasets, tables, references | Concept, Guide, Reference, Example |

FlyDocs does not use Google's tooling, their BigQuery agent, or their
data catalog types. No `pip install` of Google's package is needed.

The shared fields (`type`, `tags`) follow the same semantics. The
`title`, `description`, and `weight` fields are flydocs-specific
extensions to the OKF pattern.

As of flydocs' OKF v0.2, the `status`, `stale_after`, `generated`,
`verified`, and `sources` fields are **field-for-field aligned** with
Google's own [OKF v0.2 specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) —
same names, same types, same semantics (including the actor convention
and trust-tier derivation). This gives flydocs docs a shared vocabulary
with any other tooling built against Google's OKF, without adopting
their BigQuery-specific tooling.

## Inspiration

FlyDocs OKF is also inspired by Andrej Karpathy's
[LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
pattern — the idea that documentation should exist in three layers:

| Layer | Purpose |
|-------|---------|
| Source | The code — source of truth |
| Wiki | Human and LLM-readable documentation (markdown + frontmatter) |
| Schema | AI agent context and search index |

OKF frontmatter bridges the Wiki and Schema layers: the markdown
body is the human-readable content, while the frontmatter metadata
provides structured data for agent consumption, search indexing,
and automated navigation — without requiring a separate schema
file.
