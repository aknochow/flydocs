"""Theme resolution and template rendering."""

from __future__ import annotations

import html as html_module
import re

from jinja2 import Environment, PackageLoader
from markupsafe import Markup

from flydocs.config import Config

_env = Environment(
    loader=PackageLoader("flydocs", "templates"),
    autoescape=True,
)

_PALETTE_RE = re.compile(r"^[a-z0-9-]+$")


def _sanitize_palette(palette: str) -> str:
    """Validate palette name against safe characters."""
    if palette == "default" or _PALETTE_RE.match(palette):
        return palette
    return "default"


def resolve_html_classes(mode: str, palette: str) -> str:
    """Return the HTML element class string for theme mode and palette."""
    palette = _sanitize_palette(palette)
    classes = []
    if mode == "dark":
        classes.append("pf-v6-theme-dark")
    if palette != "default":
        classes.append(f"flydocs-palette-{palette}")
    if not classes:
        return ""
    return f' class="{" ".join(classes)}"'


def build_banner_html(config: Config) -> str:
    """Build the banner HTML if configured."""
    banner = config.theme.banner
    if not banner.text:
        return ""
    text = html_module.escape(banner.text)
    color_class = f"pf-m-{html_module.escape(banner.color)}"
    if banner.url:
        text = (
            f'<a href="{html_module.escape(banner.url)}" '
            f'style="color: inherit; text-decoration: underline;">{text}</a>'
        )
    return f'<div class="pf-v6-c-banner {color_class} pf-m-sticky flydocs-banner">{text}</div>'


_STATUS_STYLE = {"draft": "warning", "deprecated": "danger"}


def build_status_badge_html(status: str) -> str:
    """Build a status label for draft/deprecated docs. Empty for stable/unset."""
    if status not in ("draft", "deprecated"):
        return ""
    color = _STATUS_STYLE[status]
    label = html_module.escape(status)
    return (
        f'<span class="pf-v6-c-label pf-m-{color} '
        f'flydocs-status-label flydocs-status-{color}">{label}</span>'
    )


def build_deprecated_notice_html(status: str) -> str:
    """Build a deprecation notice banner when status is 'deprecated'."""
    if status != "deprecated":
        return ""
    return (
        '<div class="pf-v6-c-alert pf-m-danger flydocs-deprecated-notice">'
        "This page is <strong>deprecated</strong> and may be outdated or superseded."
        "</div>"
    )


def build_stale_notice_html(stale_after: str) -> str:
    """Build a staleness warning banner when a stale_after date is provided."""
    if not stale_after:
        return ""
    date_str = html_module.escape(stale_after)
    return (
        '<div class="pf-v6-c-alert pf-m-warning flydocs-stale-notice">'
        f"This content may be stale — last reviewed before {date_str}."
        "</div>"
    )


def build_footer_meta_html(generated_at: str) -> str:
    """Build a plain-text 'last updated' footer segment."""
    if not generated_at:
        return ""
    return f"Last updated {html_module.escape(generated_at)}"


def render_page(
    content: str,
    title: str,
    description: str,
    sidebar_html: str,
    badges_html: str,
    config: Config,
    doc_type: str = "",
    status: str = "",
    stale_after: str = "",
    generated_at: str = "",
) -> str:
    """Render a complete HTML page using Jinja2 templates."""
    mode = config.theme.mode
    palette = _sanitize_palette(config.theme.palette)
    if mode == "auto":
        theme_class = resolve_html_classes("", palette)
    else:
        theme_class = resolve_html_classes(mode, palette)

    slug = title != config.name
    tab_title = f"{title} · {config.name}" if slug else config.name

    favicon_path = "assets/img/favicon.svg"

    template = _env.get_template("page.html")
    return template.render(
        base_path=config.base_path,
        tab_title=tab_title,
        description=description,
        sidebar=Markup(sidebar_html),
        badges=Markup(badges_html),
        content=Markup(content),
        theme_class=Markup(theme_class),
        theme_mode=mode,
        palette=palette,
        banner_html=Markup(build_banner_html(config)),
        google_fonts=config.theme.google_fonts,
        project_name=config.name,
        tagline=config.theme.tagline,
        logo=config.theme.logo,
        favicon_path=favicon_path,
        github_url=config.github_url,
        sidebar_collapsible=config.sidebar.collapsible,
        doc_type=doc_type,
        search_enabled=_pagefind_available(),
        status_badge_html=Markup(build_status_badge_html(status)),
        deprecated_notice_html=Markup(build_deprecated_notice_html(status)),
        stale_notice_html=Markup(build_stale_notice_html(stale_after)),
        footer_meta_html=Markup(build_footer_meta_html(generated_at)),
    )


def _pagefind_available() -> bool:
    """Check if pagefind is importable."""
    try:
        import importlib.util

        return importlib.util.find_spec("pagefind") is not None
    except (ImportError, ModuleNotFoundError):
        return False
