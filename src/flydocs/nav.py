"""Navigation loading and sidebar HTML generation."""

from __future__ import annotations

import html as html_module

from flydocs.config import SidebarConfig
from flydocs.linker import md_to_slug, slug_to_href


def load_nav(nav_raw: list[dict] | tuple[dict, ...]) -> list[dict]:
    """Parse [[nav]] entries into a structured nav list."""
    nav = []
    for section in nav_raw:
        for section_title, items in section.items():
            if not items:
                continue
            entries = []
            for item in items:
                for label, path in item.items():
                    slug = md_to_slug(path)
                    entries.append({"label": label, "path": slug, "file": path})
            nav.append({"title": section_title, "entries": entries})
    return nav


def auto_nav_from_docs(docs_dir: str, base_path: str = "") -> list[dict]:
    """Generate navigation from directory structure and OKF frontmatter."""
    raise NotImplementedError("Auto-nav from directory structure")


def build_sidebar(
    nav: list[dict],
    current_file: str,
    base_path: str = "",
    sidebar_config: SidebarConfig | None = None,
) -> str:
    """Generate PatternFly-styled sidebar navigation HTML."""
    if sidebar_config is None:
        sidebar_config = SidebarConfig()
    esc = html_module.escape
    html = '<nav class="pf-v6-c-nav" aria-label="Documentation">\n'
    html += '  <ul class="pf-v6-c-nav__list">\n'
    for section in nav:
        title = section["title"]
        has_active = any(e["file"] == current_file for e in section["entries"])
        expanded = " pf-m-expanded" if has_active else ""
        section_expanded = sidebar_config.overrides.get(title, sidebar_config.expanded)
        is_open = section_expanded or has_active
        open_attr = " open" if is_open else ""
        html += f'    <li class="pf-v6-c-nav__item pf-m-expandable{expanded}">\n'
        html += f"      <details{open_attr}>\n"
        html += f'        <summary class="pf-v6-c-nav__link">{esc(section["title"])}\n'
        html += '          <span class="pf-v6-c-nav__toggle-icon">▸</span>\n'
        html += "        </summary>\n"
        html += '        <ul class="pf-v6-c-nav__subnav">\n'
        for entry in section["entries"]:
            href = esc(slug_to_href(entry["path"], base_path))
            active = " pf-m-current" if entry["file"] == current_file else ""
            html += '          <li class="pf-v6-c-nav__item">\n'
            html += f'            <a class="pf-v6-c-nav__link{active}" href="{href}">'
            html += f"{esc(entry['label'])}</a>\n"
            html += "          </li>\n"
        html += "        </ul>\n"
        html += "      </details>\n"
        html += "    </li>\n"
    html += "  </ul>\n"
    html += "</nav>\n"
    return html
