---
type: Reference
title: OKF Frontmatter Standard
description: The Open Knowledge Format used by flydocs for structured documentation.
tags: [okf, frontmatter, standard, metadata]
---

# OKF Frontmatter Standard

[TOC]

OKF (Open Knowledge Format) is a YAML frontmatter convention for markdown
documentation. It enables auto-generated navigation, search indexing,
linting, and type-based styling in flydocs sites.

OKF is **optional**. Flydocs builds PatternFly documentation sites from
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

Projects may add custom fields beyond these five. Flydocs ignores
fields it does not recognize.

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

This is a convention, not a requirement. Flydocs reads the `type` field
from frontmatter regardless of file location. A flat `docs/` directory
with explicit `type` fields works the same way.

When both are present, the frontmatter `type` field is authoritative.
A file at `docs/guides/setup.md` with `type: Reference` is a Reference.

## Flydocs Without OKF

Flydocs does not require OKF frontmatter. Plain markdown files produce
a PatternFly documentation site with:

- Navigation derived from file and directory names
- Page titles extracted from the first `# heading`
- No search index or type-based styling

This is the default for projects that already have markdown docs and
want a PatternFly site without restructuring their content.

## Migrating to OKF

Flydocs provides tooling to adopt OKF incrementally:

### Preview

Generate an OKF-enhanced build into a separate output directory without
modifying source files:

```bash
flydocs okf preview
```

This infers types from directory names and headings, generates suggested
frontmatter, and builds a preview site at `public-okf/`. Compare it
against your existing site to see what OKF adds.

### Init

Scaffold OKF frontmatter onto existing markdown files:

```bash
flydocs okf init docs/
```

For each `.md` file without frontmatter, this prepends a suggested
`---` block based on the filename, directory, and first heading. Files
that already have frontmatter are left unchanged.

Review the suggestions, adjust types and descriptions, then build:

```bash
flydocs build
```

### Lint

Validate OKF frontmatter across all docs:

```bash
flydocs lint
```

Reports missing required fields, unknown types, empty descriptions,
and orphan pages not in the nav.

## Relationship to Google OKF

Google's [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)
is a vendor-neutral format for representing knowledge as markdown
files with YAML frontmatter. Google's reference implementation is a
BigQuery metadata catalog tool — it extracts dataset schemas into
OKF-formatted markdown using a Python agent and Gemini enrichment.

Flydocs adopts the **format concept** from Google's OKF — markdown
files with a `---` YAML frontmatter block containing a `type` field —
but uses its own documentation-oriented type system:

| Google OKF types | Flydocs OKF types |
|-----------------|-------------------|
| datasets, tables, references | Concept, Guide, Reference, Example |

Flydocs does not use Google's tooling, their BigQuery agent, or their
data catalog types. No `pip install` of Google's package is needed.

The shared fields (`type`, `tags`) follow the same semantics. The
`title`, `description`, and `weight` fields are flydocs-specific
extensions to the OKF pattern.
