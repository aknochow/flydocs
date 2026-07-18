---
type: Reference
title: PatternFly
description: How flydocs uses PatternFly components and design tokens.
tags: [patternfly, theme, css, design-system]
---

# PatternFly

[TOC]

Flydocs generates static HTML sites styled with PatternFly,
Red Hat's open source design system. This document captures which
PatternFly features flydocs uses, how, and why.

## CSS-Only Approach

Flydocs uses PatternFly as pure CSS — no React, no JavaScript
framework. The `@patternfly/patternfly` npm package provides the
core CSS, which flydocs vendors as `patternfly-base.css` shipped
with the Python package.

Two CSS files are loaded per page:

| File | Source | Purpose |
|------|--------|---------|
| `patternfly-base.css` | Vendored from `@patternfly/patternfly` | Reset, tokens, component styles |
| `flydocs.css` | Flydocs package | Layout, sidebar, content typography |

## Semantic Tokens

Flydocs uses PatternFly semantic tokens for all color values.
Semantic tokens auto-adapt between light and dark themes — no
separate dark stylesheet needed.

Token naming convention:
```
--pf-t--[scope]--[component]--[property]--[concept]--[variant]--[state]
```

Key tokens used by flydocs:

| Purpose | Token |
|---------|-------|
| Body background | `--pf-t--global--background--color--primary--default` |
| Header background | `--pf-t--global--background--color--sticky--default` |
| Borders | `--pf-t--global--border--color--default` |
| Body text | `--pf-t--global--text--color--regular` |
| Secondary text | `--pf-t--global--text--color--subtle` |
| Links | `--pf-t--global--text--color--link--default` |
| Link hover | `--pf-t--global--text--color--link--hover` |
| Muted text | `--pf-t--global--text--color--placeholder` |
| Code blocks | `--pf-t--global--background--color--secondary--default` |
| Brand accent | `--pf-t--global--color--brand--default` |

Never use tokens ending in a number (palette/base tokens). Only use
semantic tokens.

## Dark / Light / Auto Mode

PatternFly dark mode is activated by adding `pf-v6-theme-dark` to
the `<html>` element. All semantic tokens resolve to dark values
when this class is present.

Flydocs supports three modes via `[theme] mode` in `flydocs.toml`:

| Mode | Behavior |
|------|----------|
| `dark` | Sets `class="pf-v6-theme-dark"` on `<html>`. No toggle. |
| `light` | No class (PatternFly default is light). No toggle. |
| `auto` | JavaScript checks `prefers-color-scheme` media query. Adds a toggle button in the masthead. Persists user preference to `localStorage`. |

The dark theme CSS is bundled inside `patternfly-base.css` — no
separate stylesheet is needed.

## Palettes

Flydocs ships a custom dark palette (`flydocs-dark`) with deeper
colors than stock PatternFly. This is the default palette.

| Palette | Description |
|---------|-------------|
| `default` | Stock PatternFly colors |
| `flydocs-dark` | Deeper dark theme with richer contrast (default) |

Set via `[theme] palette` in `flydocs.toml`:

```toml
[theme]
palette = "flydocs-dark"
```

Palettes only affect dark mode — light mode uses stock PatternFly
colors regardless of the palette setting.

## PatternFly Components Used

### Content (`pf-v6-c-content`)

The content wrapper class that provides PatternFly typography
defaults for headings, paragraphs, lists, tables, and inline
elements. Applied to the main content area.

### Navigation (`pf-v6-c-nav`)

Sidebar navigation using PatternFly nav classes:

| Class | Purpose |
|-------|---------|
| `.pf-v6-c-nav` | Nav container |
| `.pf-v6-c-nav__list` | Top-level nav list |
| `.pf-v6-c-nav__item` | Nav item |
| `.pf-v6-c-nav__link` | Nav link |
| `.pf-v6-c-nav__subnav` | Expandable sub-navigation |
| `.pf-m-expandable` | Modifier for expandable sections |
| `.pf-m-expanded` | Modifier for open sections |
| `.pf-m-current` | Modifier for active page |

Expandable sections use `<details>/<summary>` elements for
CSS-only expand/collapse without JavaScript.

### Banner (`pf-v6-c-banner`)

Optional announcement banner at the top of every page:

```html
<div class="pf-v6-c-banner pf-m-blue pf-m-sticky">
  This is alpha software. APIs may change.
</div>
```

Supports PatternFly banner colors: `blue`, `red`, `green`, `gold`.
Configured via `[theme.banner]` in `flydocs.toml`.

## Flydocs Layout Classes

Flydocs uses its own `flydocs-*` prefixed classes for the page
layout. This avoids collision with PatternFly component classes
while using PatternFly semantic tokens for all color values.

| Class | Purpose |
|-------|---------|
| `.flydocs-masthead` | Fixed top header |
| `.flydocs-brand` | Brand name / logo link |
| `.flydocs-tagline` | Project tagline in header |
| `.flydocs-badges` | Badge bar in header |
| `.flydocs-layout` | Flexbox container for sidebar + main |
| `.flydocs-sidebar` | Sidebar navigation panel |
| `.flydocs-main` | Main content area |
| `.flydocs-content` | Content wrapper (also uses `pf-v6-c-content`) |
| `.flydocs-toggle` | Mobile hamburger menu button |

## What Flydocs Brings Itself

PatternFly provides the design system but not everything a docs
site needs:

| Feature | PatternFly provides | Flydocs provides |
|---------|-------------------|-----------------|
| Colors and tokens | Yes | — |
| Dark/light themes | Toggle mechanism | JS for auto mode + toggle button |
| Page layout | CSS classes | HTML structure + responsive JS |
| Navigation | CSS classes + active state | Sidebar builder from config/OKF |
| Code blocks | Container styling only | Syntax highlighting (Pygments) |
| Copy button | — | JS copy-to-clipboard on `<pre>` blocks |
| Search | Input UI component only | Client-side search engine |
| Banner | Full component | Config-driven rendering |
| Responsive | Breakpoint tokens | Sidebar collapse + hamburger toggle |

## Responsive Design

At viewport widths <= 768px:

1. Sidebar is hidden by default
2. A hamburger toggle button appears in the masthead
3. Tapping the toggle slides the sidebar in as an overlay
4. Tapping outside the sidebar or pressing Escape closes it

This requires ~20 lines of JavaScript for the toggle, close-on-
backdrop, and close-on-escape behaviors. No PatternFly JavaScript
dependency.

## Fonts

PatternFly uses Red Hat Text (body) and Red Hat Mono (code). By
default, flydocs loads these from Google Fonts CDN. Set
`google_fonts = false` in `[theme]` for air-gapped deployments —
the font stack falls back to system fonts.
