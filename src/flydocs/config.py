"""Load and validate flydocs.toml configuration."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


CONFIG_FILENAMES = ("flydocs.toml", "docs.toml")


@dataclass(frozen=True)
class BannerConfig:
    text: str = ""
    color: str = "blue"
    url: str = ""


@dataclass(frozen=True)
class ThemeConfig:
    mode: str = "auto"
    palette: str = "flydocs-dark"
    logo: str = ""
    favicon: str = ""
    tagline: str = ""
    google_fonts: bool = True
    banner: BannerConfig = field(default_factory=BannerConfig)


@dataclass(frozen=True)
class Badge:
    id: str
    label: str
    url: str
    img: str


@dataclass(frozen=True)
class SidebarConfig:
    expanded: bool = True
    collapsible: bool = True
    overrides: dict[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class ReadmeConfig:
    enabled: bool = False
    output: str = "README.md"


@dataclass(frozen=True)
class Config:
    name: str = "Documentation"
    url: str = ""
    github_url: str = ""
    description: str = ""
    docs_dir: str = "docs"
    site_dir: str = "public"
    base_path: str = ""
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    sidebar: SidebarConfig = field(default_factory=SidebarConfig)
    readme: ReadmeConfig = field(default_factory=ReadmeConfig)
    badges: tuple[Badge, ...] = ()
    nav: tuple[dict, ...] = ()


def find_config(start_dir: str | Path = ".") -> Path | None:
    """Find the config file in the given directory."""
    start = Path(start_dir)
    for name in CONFIG_FILENAMES:
        path = start / name
        if path.exists():
            return path
    return None


def load_config(config_path: str | Path | None = None) -> Config:
    """Load and validate configuration from a TOML file."""
    if config_path is None:
        config_path = find_config()
    if config_path is None:
        return Config()

    path = Path(config_path)
    try:
        with open(path, "rb") as f:
            raw = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise SystemExit(f"Error: invalid TOML in {path}: {exc}") from exc
    except FileNotFoundError:
        raise SystemExit(f"Error: config file not found: {path}") from None

    project = raw.get("project", {})
    theme_raw = raw.get("theme", {})
    banner_raw = theme_raw.get("banner", {})
    badges_raw = raw.get("badges", [])
    nav_raw = raw.get("nav", [])

    banner = BannerConfig(
        text=str(banner_raw.get("text", "")),
        color=str(banner_raw.get("color", "blue")),
        url=str(banner_raw.get("url", "")),
    )

    theme = ThemeConfig(
        mode=str(theme_raw.get("mode", "auto")),
        palette=str(theme_raw.get("palette", "flydocs-dark")),
        logo=str(theme_raw.get("logo", "")),
        favicon=str(theme_raw.get("favicon", "")),
        tagline=str(theme_raw.get("tagline", "")),
        google_fonts=bool(theme_raw.get("google_fonts", True)),
        banner=banner,
    )

    badges = tuple(
        Badge(
            id=str(b.get("id", "")),
            label=str(b.get("label", "")),
            url=str(b.get("url", "")),
            img=str(b.get("img", "")),
        )
        for b in badges_raw
        if b.get("id") and b.get("label") and b.get("img")
    )

    sidebar_raw = raw.get("sidebar", {})
    sidebar_overrides = sidebar_raw.get("overrides", {})
    sidebar = SidebarConfig(
        expanded=bool(sidebar_raw.get("expanded", True)),
        collapsible=bool(sidebar_raw.get("collapsible", True)),
        overrides={str(k): bool(v) for k, v in sidebar_overrides.items()},
    )

    readme_raw = raw.get("readme", {})
    readme_config = ReadmeConfig(
        enabled=bool(readme_raw.get("enabled", False)),
        output=str(readme_raw.get("output", "README.md")),
    )

    base_path = os.environ.get("DOCS_BASE_PATH", str(project.get("base_path", "")))
    base_path = base_path.rstrip("/")

    return Config(
        name=str(project.get("name", "Documentation")),
        url=str(project.get("url", "")),
        github_url=str(project.get("github_url", "")),
        description=str(project.get("description", "")),
        docs_dir=str(project.get("docs_dir", "docs")),
        site_dir=str(project.get("site_dir", "public")),
        base_path=base_path,
        theme=theme,
        sidebar=sidebar,
        readme=readme_config,
        badges=badges,
        nav=tuple(nav_raw),
    )
