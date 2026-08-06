[![docs](https://img.shields.io/badge/docs-online-blue)](https://aknochow.github.io/flydocs/) [![aknochow/flydocs](https://img.shields.io/github/actions/workflow/status/aknochow/flydocs/test.yml?label=aknochow%2Fflydocs)](https://github.com/aknochow/flydocs) [![OKF](https://img.shields.io/badge/OKF-v0.2-blueviolet)](https://aknochow.github.io/flydocs/okf/) [![PatternFly](https://img.shields.io/badge/PatternFly-v6-EE0000)](https://www.patternfly.org/)

# FlyDocs

Static documentation sites with PatternFly from markdown.

FlyDocs takes your markdown files and generates a complete
documentation site with Red Hat's PatternFly design system.
Dark mode, light mode, responsive layout, search, and navigation
all work out of the box.

## Features

- **PatternFly** — Red Hat's open source design system, CSS-only
- **Dark / Light / Auto** — respects system preference with manual toggle
- **OKF frontmatter** — optional structured metadata for auto-nav and search
- **Plain markdown works** — no frontmatter required to get a site
- **Badges** — define once in config, reference anywhere in docs
- **Responsive** — works on desktop, tablet, and phone
- **Lint** — validate frontmatter, navigation, and links
- **Zero JavaScript frameworks** — vanilla JS for toggle and copy

## Install

```bash
pip install flydocs
```

## Quick Start

1. Create a `docs/` directory with markdown files:

```
docs/
  index.md
  quickstart.md
  reference/
    api.md
```

2. Create `flydocs.toml` in your project root:

```toml
[project]
name = "My Project"
```

3. Build and preview:

```bash
flydocs preview
```

Your site is at `http://localhost:8000`.

## Add OKF Frontmatter (Optional)

Add structured metadata to your docs for richer navigation and search:

```yaml
---
type: Guide
title: Quick Start
description: Get up and running in 5 minutes.
tags: [quickstart, install]
---
```

OKF v0.2 also adds optional `status`, `stale_after`, `generated`,
`verified`, and `sources` fields for lifecycle and provenance tracking,
aligned with [Google's OKF v0.2 spec](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

See the [OKF Frontmatter](https://aknochow.github.io/flydocs/okf/) reference for the full spec.

## Commands

| Command | Description |
|---------|-------------|
| `flydocs build` | Build the documentation site |
| `flydocs preview` | Build and preview locally |
| `flydocs lint` | Validate frontmatter, nav, and links |
| `flydocs search QUERY` | Search docs by metadata |
| `flydocs init PATH` | Scaffold a new doc with OKF frontmatter |
| `flydocs badges` | Print badge markdown for README |
| `flydocs readme` | Generate README.md from docs/index.md |
| `flydocs okf preview` | Preview OKF-enhanced build *(planned, not yet implemented)* |
| `flydocs okf init` | Add OKF frontmatter to existing docs *(planned, not yet implemented)* |

## Configuration

See the [Configuration](https://aknochow.github.io/flydocs/configuration/) reference for the full
`flydocs.toml` spec.

---

*Generated from `docs/index.md` by [flydocs](https://github.com/aknochow/flydocs).*
