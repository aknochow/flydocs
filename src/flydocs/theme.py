"""Theme resolution and template rendering."""

from __future__ import annotations

import html as html_module
import re

from jinja2 import Environment, PackageLoader

from flydocs.config import Config

_env = Environment(
    loader=PackageLoader("flydocs", "templates"),
    autoescape=False,
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
        text = f'<a href="{html_module.escape(banner.url)}" style="color: inherit; text-decoration: underline;">{text}</a>'
    return f'<div class="pf-v6-c-banner {color_class} pf-m-sticky flydocs-banner">{text}</div>'


def render_page(
    content: str,
    title: str,
    description: str,
    sidebar_html: str,
    badges_html: str,
    config: Config,
    doc_type: str = "",
) -> str:
    """Render a complete HTML page using Jinja2 templates."""
    mode = config.theme.mode
    palette = _sanitize_palette(config.theme.palette)
    if mode == "auto":
        theme_class = resolve_html_classes("", palette)
    else:
        theme_class = resolve_html_classes(mode, palette)

    slug = title != config.name
    tab_title = (
        f"{html_module.escape(title)} · {html_module.escape(config.name)}"
        if slug
        else html_module.escape(config.name)
    )

    favicon_path = "assets/img/favicon.svg"

    template = _env.get_template("page.html")
    return template.render(
        base_path=html_module.escape(config.base_path),
        tab_title=tab_title,
        description=html_module.escape(description),
        sidebar=sidebar_html,
        badges=badges_html,
        content=content,
        theme_class=theme_class,
        theme_mode=mode,
        palette=html_module.escape(palette),
        banner_html=build_banner_html(config),
        google_fonts=config.theme.google_fonts,
        project_name=html_module.escape(config.name),
        tagline=html_module.escape(config.theme.tagline),
        logo=html_module.escape(config.theme.logo),
        favicon_path=favicon_path,
        github_url=html_module.escape(config.github_url),
        sidebar_collapsible=config.sidebar.collapsible,
        doc_type=html_module.escape(doc_type),
    )
