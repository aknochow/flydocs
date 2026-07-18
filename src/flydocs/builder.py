"""Core build orchestration — markdown to HTML site generation."""

from __future__ import annotations

import os
import shutil
from importlib import resources
from pathlib import Path

import markdown

from flydocs.badges import build_badge_html, expand_inline_badges
from flydocs.config import Config
from flydocs.frontmatter import extract_title, parse_frontmatter
from flydocs.linker import md_to_slug, rewrite_links
from flydocs.nav import build_sidebar, load_nav
from flydocs.theme import render_page


def collect_md_files(docs_dir: str) -> list[str]:
    """Walk docs directory and return sorted list of .md paths relative to docs_dir."""
    md_files = []
    for root, dirs, files in os.walk(docs_dir):
        dirs.sort()
        for fname in sorted(files):
            if fname.endswith(".md"):
                rel = os.path.relpath(os.path.join(root, fname), docs_dir)
                md_files.append(rel.replace("\\", "/"))
    return md_files


def _copy_package_assets(site_dir: str) -> None:
    """Copy CSS, JS, and default favicon from package data to the site directory."""
    assets_ref = resources.files("flydocs") / "assets"

    for subdir in ("css", "js", "img"):
        src_dir = assets_ref / subdir
        dst_dir = os.path.join(site_dir, "assets", subdir)
        os.makedirs(dst_dir, exist_ok=True)
        for item in src_dir.iterdir():
            if item.is_file():
                dst = os.path.join(dst_dir, item.name)
                with open(dst, "wb") as f:
                    f.write(item.read_bytes())


def build_page(
    md_rel: str,
    config: Config,
    nav: list[dict],
    badges_html: str,
    md_converter: markdown.Markdown,
) -> None:
    """Build a single page from a markdown file."""
    with open(os.path.join(config.docs_dir, md_rel)) as f:
        raw = f.read()

    meta, body = parse_frontmatter(raw)
    title = extract_title(meta, body, fallback=config.name)
    description = meta.get("description", config.description)

    body = expand_inline_badges(body, config.badges)

    content = md_converter.convert(body)
    md_converter.reset()

    content = rewrite_links(content, md_rel, config.base_path)
    sidebar = build_sidebar(nav, md_rel, config.base_path, config.sidebar)

    html = render_page(
        content=content,
        title=title,
        description=description,
        sidebar_html=sidebar,
        badges_html=badges_html,
        config=config,
    )

    slug = md_to_slug(md_rel)
    if not slug:
        out_path = os.path.join(config.site_dir, "index.html")
    else:
        out_dir = os.path.join(config.site_dir, slug)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "index.html")

    with open(out_path, "w") as f:
        f.write(html)

    display = "/" if not slug else f"/{slug}/"
    print(f"  + {display}")


def _validate_site_dir(site_dir: str) -> None:
    """Ensure site_dir is a relative path contained within the project root."""
    resolved = Path(site_dir).resolve()
    project_root = Path.cwd().resolve()
    if not str(resolved).startswith(str(project_root) + os.sep) and resolved != project_root:
        raise SystemExit(f"Error: site_dir '{site_dir}' escapes project root")


def build_site(config: Config, clean: bool = False) -> None:
    """Build the complete documentation site."""
    _validate_site_dir(config.site_dir)
    if clean and os.path.exists(config.site_dir):
        shutil.rmtree(config.site_dir)

    os.makedirs(config.site_dir, exist_ok=True)

    nav = load_nav(config.nav)
    badges_html = build_badge_html(config.badges)

    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "codehilite", "toc"],
        extension_configs={
            "codehilite": {"css_class": "highlight", "guess_lang": False},
            "toc": {"permalink": "#", "permalink_class": "flydocs-anchor"},
        },
    )

    print("Build started")

    md_files = collect_md_files(config.docs_dir)
    for md_rel in md_files:
        build_page(md_rel, config, nav, badges_html, md)

    _copy_package_assets(config.site_dir)

    if config.theme.favicon and os.path.exists(config.theme.favicon):
        dst = os.path.join(config.site_dir, "assets", "img", "favicon.svg")
        shutil.copy2(config.theme.favicon, dst)

    if config.readme.enabled:
        from flydocs.readme import generate_readme

        readme_content = generate_readme(config)
        with open(config.readme.output, "w") as f:
            f.write(readme_content)
        print(f"  + {config.readme.output}")

    print(f"Build finished ({len(md_files)} pages)")
