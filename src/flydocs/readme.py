"""Write a README entrypoint from the docs index, or leave an index symlink alone."""

from __future__ import annotations

import errno
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path

from flydocs.badges import badges_markdown
from flydocs.config import Config
from flydocs.frontmatter import parse_frontmatter


@dataclass(frozen=True)
class ReadmeSymlink:
    """How the configured README path relates to docs/index.md."""

    state: str
    message: str = ""


def _docs_dir(config: Config) -> Path:
    docs = Path(config.docs_dir)
    if not docs.is_absolute():
        docs = Path.cwd() / docs
    return docs


def _repo_root(config: Config) -> Path:
    """Directory that contains docs_dir. Symlinks may not leave it."""
    return _docs_dir(config).resolve().parent


def _output_path(config: Config, output: str | None) -> Path:
    path = Path(output or config.readme.output)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def _index_path(config: Config) -> Path:
    return _docs_dir(config) / "index.md"


def _resolve_symlink(path: Path, root: Path) -> Path:
    """Follow a symlink chain. Reject loops and targets outside root."""
    seen: set[str] = set()
    current = path
    try:
        while current.is_symlink():
            key = str(current.absolute())
            if key in seen:
                raise ValueError(f"{path.name} is a symlink loop")
            seen.add(key)
            raw = os.readlink(current)
            nxt = Path(raw)
            if not nxt.is_absolute():
                nxt = current.parent / nxt
            current = Path(os.path.normpath(nxt))
        resolved = current.resolve(strict=True)
    except ValueError:
        raise
    except RuntimeError:
        raise ValueError(f"{path.name} is a symlink loop") from None
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ValueError(f"{path.name} is a symlink loop") from None
        if exc.errno == errno.ENOENT:
            raise ValueError(f"{path.name} symlink target does not exist ({current})") from None
        raise ValueError(f"{path.name} symlink could not be resolved: {exc.strerror}") from None
    root_resolved = root.resolve()
    if not resolved.is_relative_to(root_resolved):
        raise ValueError(f"{path.name} symlink leaves the repository ({resolved})")
    return resolved


def inspect_readme_symlink(config: Config, output: str | None = None) -> ReadmeSymlink:
    """Classify the README path.

    ``ok`` is a symlink to ``docs/index.md``. ``bad`` is a symlink that loops,
    leaves the repository, or points somewhere else. ``plain`` is a regular
    file or a path that does not exist yet.
    """
    path = _output_path(config, output)
    if not path.is_symlink():
        return ReadmeSymlink("plain")
    root = _repo_root(config)
    try:
        resolved = _resolve_symlink(path, root)
    except ValueError as exc:
        return ReadmeSymlink("bad", str(exc))
    index = _index_path(config).resolve()
    if resolved != index:
        actual = os.path.relpath(resolved, root)
        expected = os.path.relpath(index, root)
        return ReadmeSymlink(
            "bad",
            f"{path.name} symlink points at {actual}, expected {expected}",
        )
    shown = output or config.readme.output
    return ReadmeSymlink(
        "ok",
        f"{shown} is a symlink to {config.docs_dir}/index.md; leaving it unchanged",
    )


def publish_readme(config: Config, output: str | None = None, dry_run: bool = False) -> str:
    """Write a generated README, or leave a valid index symlink unchanged.

    A bad symlink is an error. Generation does not replace it.
    """
    status = inspect_readme_symlink(config, output)
    if status.state == "bad":
        raise SystemExit(f"Error: {status.message}")
    if status.state == "ok":
        return status.message
    content = generate_readme(config)
    if dry_run:
        return content
    _write_readme_no_follow(_output_path(config, output), content)
    return f"Generated {output or config.readme.output}"


def _write_readme_no_follow(dest: Path, content: str) -> None:
    """Replace dest by name. A symlink at that path is replaced, not followed.

    The temporary file is created mode 0600. Restore the previous mode of a
    regular file, or 0644 when the path is new or a symlink, before replacing
    the name.
    """
    directory = dest.parent
    mode = 0o644
    try:
        info = dest.lstat()
    except OSError:
        info = None
    if info is not None and not stat.S_ISLNK(info.st_mode):
        mode = stat.S_IMODE(info.st_mode)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{dest.name}.", suffix=".tmp", dir=directory)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(content)
            handle.flush()
            os.fchmod(handle.fileno(), mode)
        os.replace(tmp_path, dest)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except OSError:
                pass


def generate_readme(config: Config) -> str:
    """Write a short README that points at the documentation.

    The docs index stays the OKF page. The README is a separate entrypoint
    for the repository home page: title, description, badges, and links.
    It does not copy the index body.
    """
    index_path = os.path.join(config.docs_dir, "index.md")
    if not os.path.exists(index_path):
        raise SystemExit(f"Error: {index_path} not found")

    with open(index_path) as f:
        raw = f.read()

    meta, _body = parse_frontmatter(raw)
    title = str(meta.get("title") or config.name)
    description = str(meta.get("description") or config.description or "")
    docs_index = f"{config.docs_dir}/index.md"
    badge_line = badges_markdown(config.badges)

    parts = []
    if badge_line:
        parts.append(badge_line)
        parts.append("")
    parts.append(f"# {title}")
    parts.append("")
    if description:
        parts.append(description)
        parts.append("")
    parts.append("## Documentation")
    parts.append("")
    if config.url:
        site = config.url if config.url.endswith("/") else config.url + "/"
        parts.append(f"The documentation site: [{site}]({site})")
        parts.append("")
    parts.append(f"Source: [{docs_index}]({docs_index})")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append(
        f"*Generated from `{config.docs_dir}/index.md` by "
        f"[flydocs](https://github.com/aknochow/flydocs).*"
    )
    parts.append("")

    return "\n".join(parts)


def _rewrite_doc_links(body: str, site_url: str) -> str:
    """Rewrite relative .md links to point at the docs site."""
    base = site_url.rstrip("/")

    def replace(m: re.Match) -> str:
        text = m.group(1)
        path = m.group(2)
        frag = m.group(3) or ""
        parts = path.replace(".md", "").split("/")
        if parts[-1] == "index":
            parts = parts[:-1]
        slug = "/".join(parts).strip("/")
        if slug:
            return f"[{text}]({base}/{slug}/{frag})"
        return f"[{text}]({base}/{frag})"

    return re.sub(r"\[([^\]]+)\]\(([^)#:]+)\.md(#[^)]*)?\)", replace, body)
