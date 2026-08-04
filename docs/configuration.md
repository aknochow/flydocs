---
type: Reference
title: Configuration
description: Complete reference for the flydocs.toml configuration file.
tags: [config, toml, settings, theme, badges, nav]
status: stable
generated:
  by: human:aknochow
  at: 2026-08-03T00:00:00Z
---

# Configuration

[TOC]

FlyDocs is configured via `flydocs.toml` in the project root. All
fields are optional except `[project] name`. If no config file is
found, flydocs uses sensible defaults.

For backward compatibility, flydocs also reads `docs.toml` if
`flydocs.toml` is not present.

## `[project]`

Core project settings.

```toml
[project]
name = "My Project"
url = "https://example.github.io/my-project/"
description = "Project documentation."
docs_dir = "docs"
site_dir = "public"
base_path = "/my-project"
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `name` | string | `"Documentation"` | Project name. Used in page titles and masthead. |
| `url` | string | `""` | Canonical site URL. |
| `description` | string | `""` | Default HTML meta description. |
| `docs_dir` | string | `"docs"` | Directory containing markdown source files. |
| `site_dir` | string | `"public"` | Output directory for the built site. |
| `base_path` | string | `""` | URL prefix for deployment in subdirectories. The `DOCS_BASE_PATH` environment variable overrides this value. |

## `[theme]`

Visual appearance settings. FlyDocs follows PatternFly design
standards — colors are not user-configurable. The theme section
controls mode, branding, and optional UI elements.

```toml
[theme]
mode = "auto"
palette = "flydocs-dark"
logo = "docs/assets/logo.svg"
favicon = "docs/assets/favicon.svg"
tagline = "Your project tagline"
google_fonts = true
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `mode` | string | `"auto"` | Theme mode: `"dark"`, `"light"`, or `"auto"`. Auto detects system preference and shows a toggle. |
| `palette` | string | `"flydocs-dark"` | Dark mode color palette: `"default"` (stock PatternFly) or `"flydocs-dark"` (deeper dark theme). |
| `logo` | string | `""` | Path to a logo image (SVG or PNG) displayed in the masthead. |
| `favicon` | string | `""` | Path to a favicon. FlyDocs ships a default if not set. |
| `tagline` | string | `""` | Short text shown next to the project name in the masthead. |
| `google_fonts` | bool | `true` | Load Red Hat Text and Red Hat Mono from Google Fonts CDN. Set to `false` for air-gapped or privacy-conscious deployments. |

## `[theme.banner]`

Optional announcement banner displayed at the top of every page.
Uses the PatternFly Banner component.

```toml
[theme.banner]
text = "Beta — APIs may change without notice."
color = "blue"
url = "https://github.com/example/releases"
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `text` | string | `""` | Banner message. Empty string disables the banner. |
| `color` | string | `"blue"` | PatternFly banner color: `"blue"`, `"red"`, `"green"`, `"gold"`. |
| `url` | string | `""` | If set, the banner becomes a link. |

## `[readme]`

Optionally generate `README.md` from `docs/index.md` during build.
The generated README strips OKF frontmatter, expands inline badges,
rewrites doc links to point at the docs site URL, and appends a
footer attribution.

```toml
[readme]
enabled = true
output = "README.md"
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled` | bool | `false` | Generate README during `flydocs build`. |
| `output` | string | `"README.md"` | Output file path for the generated README. |

When enabled, `flydocs build` auto-generates the README. You can
also run `flydocs readme` manually at any time, regardless of this
setting.

This is optional — projects that maintain their README independently
can leave this disabled.

## `[[badges]]`

Badges are defined as an array of tables. Each badge appears in the
site header and can be referenced inline in markdown content.

```toml
[[badges]]
id = "version"
label = "v0.1.0"
url = "https://github.com/example/releases"
img = "https://img.shields.io/badge/version-v0.1.0-orange"

[[badges]]
id = "docs"
label = "Docs"
url = "https://example.github.io/my-project/"
img = "https://img.shields.io/badge/docs-online-blue"
```

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `id` | string | Yes | Unique identifier for inline references. |
| `label` | string | Yes | Alt text and aria-label for accessibility. |
| `url` | string | Yes | Link target when the badge is clicked. |
| `img` | string | Yes | Badge image URL (typically shields.io). |

### Inline Badge References

Use badges anywhere in your markdown content:

```markdown
Current version: {{badge:version}}

All project badges: {{badges}}
```

- `{{badge:id}}` expands to a single badge as a linked image.
- `{{badges}}` expands to the full badge bar.

### README Badge Markdown

Generate copy-pasteable badge markdown for your README:

```bash
flydocs badges
```

## `[sidebar]`

Controls the sidebar navigation behavior. By default, all sections
are expanded.

```toml
[sidebar]
expanded = true
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `expanded` | bool | `true` | Default expand state for all nav sections. Set to `false` to collapse all sections by default. |

### Per-Section Overrides

Override the default expand state for individual sections using
`[sidebar.overrides]`. The key is the section title from `[[nav]]`,
and the value is a boolean.

```toml
[sidebar]
expanded = true

[sidebar.overrides]
"Reference" = false
"Help" = false
```

In this example, all sections start expanded except "Reference" and
"Help", which start collapsed. Users can still click to expand them.

The active section (containing the current page) is always expanded
regardless of the override setting.

### Examples

Expand everything (default):

```toml
[sidebar]
expanded = true
```

Collapse everything except the active section:

```toml
[sidebar]
expanded = false
```

Expand everything but collapse specific sections:

```toml
[sidebar]
expanded = true

[sidebar.overrides]
"API Reference" = false
"Changelog" = false
```

Collapse everything but expand specific sections:

```toml
[sidebar]
expanded = false

[sidebar.overrides]
"Getting Started" = true
"Guides" = true
```

## `[[nav]]`

Explicit navigation structure. When present, the sidebar follows
this order exactly. When absent, flydocs auto-generates navigation
from the directory structure and OKF frontmatter.

```toml
[[nav]]
"Getting Started" = [
    { "Introduction" = "index.md" },
    { "Quick Start" = "quickstart.md" },
]

[[nav]]
"Guides" = [
    { "Installation" = "guides/installation.md" },
    { "Configuration" = "guides/configuration.md" },
]

[[nav]]
"Reference" = [
    { "API" = "reference/api.md" },
    { "CLI" = "reference/cli.md" },
]
```

Each `[[nav]]` entry defines a collapsible section in the sidebar.
The key is the section title. The value is an array of page entries,
where each entry maps a display label to a markdown file path
relative to `docs_dir`.

### Auto-Generated Navigation

When `[[nav]]` is omitted, flydocs generates navigation from the
file system:

1. Top-level directories become sections (capitalized).
2. Files within each directory become entries.
3. Display labels are derived from OKF `title` frontmatter, falling
   back to the filename.
4. Entries are sorted by OKF `weight` (ascending), then alphabetically.
5. `index.md` files become the first entry in their section.

## Complete Example

```toml
[project]
name = "OGO"
url = "https://aknochow.github.io/ogo/"
docs_dir = "docs"
site_dir = "public"

[theme]
mode = "auto"
tagline = "OpenShell Gateway Operator"
google_fonts = true

[theme.banner]
text = "Alpha — APIs may change without notice."
color = "gold"

[sidebar]
expanded = true

[sidebar.overrides]
"Reference" = false

[[badges]]
id = "version"
label = "Version"
url = "https://github.com/aknochow/ogo/releases"
img = "https://img.shields.io/badge/version-v0.1.0-orange"

[[badges]]
id = "docs"
label = "Docs"
url = "https://aknochow.github.io/ogo/"
img = "https://img.shields.io/badge/docs-online-blue?logo=readthedocs&logoColor=white"

[[nav]]
"Overview" = [
    { "Introduction" = "index.md" },
]

[[nav]]
"Concepts" = [
    { "Overview" = "concepts/index.md" },
    { "Gateway" = "concepts/gateway.md" },
    { "Sandbox" = "concepts/sandbox.md" },
]

[[nav]]
"Guides" = [
    { "Quickstart" = "guides/quickstart.md" },
]

[[nav]]
"Reference" = [
    { "OpenShellGateway" = "reference/openshellgateway.md" },
]
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DOCS_BASE_PATH` | Overrides `[project] base_path`. Used in CI for deployment subdirectories. |
