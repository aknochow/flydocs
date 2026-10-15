"""Tests for README generation and the docs-index symlink."""

from __future__ import annotations

import os
import stat

import pytest

from flydocs.config import Config, ReadmeConfig
from flydocs.readme import (
    _rewrite_doc_links,
    _write_readme_no_follow,
    generate_readme,
    inspect_readme_symlink,
    publish_readme,
)


class TestRewriteDocLinks:
    def test_basic_rewrite(self):
        body = "[Config](configuration.md)"
        result = _rewrite_doc_links(body, "https://example.com")
        assert result == "[Config](https://example.com/configuration/)"

    def test_index_becomes_root(self):
        body = "[Home](index.md)"
        result = _rewrite_doc_links(body, "https://example.com")
        assert result == "[Home](https://example.com/)"

    def test_preserves_non_index_with_index_substring(self):
        body = "[Reindex](reindex.md)"
        result = _rewrite_doc_links(body, "https://example.com")
        assert "reindex" in result
        assert result == "[Reindex](https://example.com/reindex/)"

    def test_nested_index(self):
        body = "[Guide](guides/index.md)"
        result = _rewrite_doc_links(body, "https://example.com")
        assert result == "[Guide](https://example.com/guides/)"

    def test_fragment_preserved(self):
        body = "[Theme](config.md#theme)"
        result = _rewrite_doc_links(body, "https://example.com")
        assert "#theme" in result

    def test_external_links_untouched(self):
        body = "[GitHub](https://github.com)"
        result = _rewrite_doc_links(body, "https://example.com")
        assert result == "[GitHub](https://github.com)"


class TestGenerateReadme:
    def test_strips_frontmatter(self, sample_config):
        content = generate_readme(sample_config)
        assert "---" not in content.split("\n")[0]
        assert "type: Guide" not in content

    def test_includes_body(self, sample_config):
        content = generate_readme(sample_config)
        assert "Test Project" in content

    def test_includes_attribution(self, sample_config):
        content = generate_readme(sample_config)
        assert "Generated from" in content
        assert "flydocs" in content

    def test_rewrites_links(self, sample_config):
        content = generate_readme(sample_config)
        assert "](okf.md)" not in content
        assert "example.com" in content or ".md" in content

    def test_missing_index_exits(self, tmp_path):
        from flydocs.config import Config

        config = Config(docs_dir=str(tmp_path / "empty"))
        import pytest

        with pytest.raises(SystemExit, match="not found"):
            generate_readme(config)

    def test_includes_badges(self, tmp_path):
        from flydocs.config import Badge, Config

        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "index.md").write_text("---\ntype: Guide\ntitle: T\ndescription: D\n---\n# T\n")
        config = Config(
            name="T",
            docs_dir=str(docs),
            badges=(Badge(id="v", label="v1", url="https://x", img="https://i"),),
        )
        content = generate_readme(config)
        assert "[![v1]" in content


def _project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text(
        "---\ntype: Guide\ntitle: T\ndescription: D\n---\n# T\n\nSee [next](getting-started.md).\n"
    )
    (docs / "getting-started.md").write_text(
        "---\ntype: Guide\ntitle: Start\ndescription: S\n---\n# Start\n"
    )
    return Config(name="T", docs_dir="docs", site_dir="public", readme=ReadmeConfig(enabled=True))


class TestReadmeSymlink:
    def test_valid_symlink_is_left_unchanged(self, tmp_path, monkeypatch):
        config = _project(tmp_path, monkeypatch)
        os.symlink("docs/index.md", "README.md")
        message = publish_readme(config)
        assert "leaving it unchanged" in message
        assert os.readlink("README.md") == "docs/index.md"
        assert "type: Guide" in (tmp_path / "docs" / "index.md").read_text()

    def test_dry_run_does_not_rewrite_symlink(self, tmp_path, monkeypatch):
        config = _project(tmp_path, monkeypatch)
        os.symlink("docs/index.md", "README.md")
        message = publish_readme(config, dry_run=True)
        assert "leaving it unchanged" in message
        assert os.readlink("README.md") == "docs/index.md"

    def test_regular_file_is_still_generated(self, tmp_path, monkeypatch):
        config = _project(tmp_path, monkeypatch)
        config = Config(
            name="T",
            url="https://example.com/docs/",
            docs_dir="docs",
            site_dir="public",
            readme=ReadmeConfig(enabled=True),
        )
        message = publish_readme(config)
        assert message == "Generated README.md"
        text = (tmp_path / "README.md").read_text()
        assert "type: Guide" not in text
        assert "getting-started.md" not in text
        assert "example.com/docs/getting-started/" in text
        assert "Generated from" in text

    def test_wrong_target_is_an_error(self, tmp_path, monkeypatch):
        config = _project(tmp_path, monkeypatch)
        os.symlink("docs/getting-started.md", "README.md")
        with pytest.raises(SystemExit, match="points at"):
            publish_readme(config)
        assert os.readlink("README.md") == "docs/getting-started.md"

    def test_loop_is_an_error(self, tmp_path, monkeypatch):
        config = _project(tmp_path, monkeypatch)
        os.symlink("README.md", "README.md")
        with pytest.raises(SystemExit, match="symlink loop"):
            publish_readme(config)

    def test_escape_is_an_error(self, tmp_path, monkeypatch):
        config = _project(tmp_path, monkeypatch)
        os.symlink("/etc/passwd", "README.md")
        with pytest.raises(SystemExit, match="leaves the repository"):
            publish_readme(config)

    def test_long_symlink_chain_to_index_is_ok(self, tmp_path, monkeypatch):
        config = _project(tmp_path, monkeypatch)
        target = "docs/index.md"
        for i in range(20, 0, -1):
            os.symlink(target, tmp_path / f"l{i}")
            target = f"l{i}"
        os.symlink("l1", tmp_path / "README.md")
        message = publish_readme(config)
        assert "leaving it unchanged" in message
        assert os.readlink(tmp_path / "README.md") == "l1"

    def test_inspect_plain_file(self, tmp_path, monkeypatch):
        config = _project(tmp_path, monkeypatch)
        assert inspect_readme_symlink(config).state == "plain"

    def test_directory_symlink_loop_is_an_error(self, tmp_path, monkeypatch):
        config = _project(tmp_path, monkeypatch)
        os.symlink("loop", tmp_path / "loop")
        os.symlink("loop/index.md", tmp_path / "README.md")
        with pytest.raises(SystemExit, match="symlink loop"):
            publish_readme(config)

    def test_unreadable_symlink_reports_the_os_error(self, tmp_path, monkeypatch):
        config = _project(tmp_path, monkeypatch)
        blocked = tmp_path / "blocked"
        blocked.mkdir()
        (blocked / "index.md").write_text("secret\n")
        blocked.chmod(0)
        os.symlink("blocked/index.md", tmp_path / "README.md")
        try:
            with pytest.raises(SystemExit, match="could not be resolved") as raised:
                publish_readme(config)
            assert "does not exist" not in str(raised.value)
        finally:
            blocked.chmod(0o755)

    def test_write_replaces_symlink_instead_of_following_it(self, tmp_path):
        secret = tmp_path / "secret"
        secret.write_text("keep")
        dest = tmp_path / "README.md"
        os.symlink(secret, dest)
        _write_readme_no_follow(dest, "generated\n")
        assert secret.read_text() == "keep"
        assert dest.read_text() == "generated\n"
        assert not dest.is_symlink()
        assert stat.S_IMODE(dest.stat().st_mode) == 0o644

    def test_generated_readme_keeps_existing_mode(self, tmp_path, monkeypatch):
        config = _project(tmp_path, monkeypatch)
        readme = tmp_path / "README.md"
        readme.write_text("old\n")
        readme.chmod(0o644)
        publish_readme(config)
        assert stat.S_IMODE(readme.stat().st_mode) == 0o644

    def test_new_readme_is_world_readable(self, tmp_path, monkeypatch):
        _project(tmp_path, monkeypatch)
        publish_readme(
            Config(name="T", docs_dir="docs", site_dir="public", readme=ReadmeConfig(enabled=True))
        )
        mode = stat.S_IMODE((tmp_path / "README.md").stat().st_mode)
        assert mode & 0o044 == 0o044
