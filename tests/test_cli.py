"""CLI integration tests."""

from __future__ import annotations

import os

from click.testing import CliRunner

from flydocs.cli import main


class TestCli:
    def test_help(self):
        result = CliRunner().invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Static documentation sites" in result.output

    def test_version(self):
        result = CliRunner().invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "flydocs" in result.output

    def test_all_commands_listed(self):
        result = CliRunner().invoke(main, ["--help"])
        for cmd in ("build", "preview", "lint", "search", "init", "badges", "readme", "okf"):
            assert cmd in result.output, f"Command '{cmd}' not in --help output"


class TestBuildCli:
    def test_build(self, sample_config, monkeypatch):
        monkeypatch.chdir(os.path.dirname(sample_config.docs_dir))
        cfg = os.path.join(os.path.dirname(sample_config.docs_dir), "flydocs.toml")
        with open(cfg, "w") as f:
            f.write(
                f'[project]\nname = "Test"\ndocs_dir = "{sample_config.docs_dir}"\n'
                f'site_dir = "{sample_config.site_dir}"\n'
                '[[nav]]\n"Overview" = [{"Home" = "index.md"}]\n'
            )
        result = CliRunner().invoke(main, ["build", "--config", cfg])
        assert result.exit_code == 0
        assert "Build finished" in result.output


class TestLintCli:
    def test_lint_passes(self, sample_config, monkeypatch):
        monkeypatch.chdir(os.path.dirname(sample_config.docs_dir))
        cfg = os.path.join(os.path.dirname(sample_config.docs_dir), "flydocs.toml")
        with open(cfg, "w") as f:
            f.write(f'[project]\nname = "Test"\ndocs_dir = "{sample_config.docs_dir}"\n')
        result = CliRunner().invoke(main, ["lint", "--config", cfg])
        assert result.exit_code == 0
        assert "Lint passed" in result.output


class TestSearchCli:
    def test_search_finds(self, sample_config, monkeypatch):
        monkeypatch.chdir(os.path.dirname(sample_config.docs_dir))
        cfg = os.path.join(os.path.dirname(sample_config.docs_dir), "flydocs.toml")
        with open(cfg, "w") as f:
            f.write(f'[project]\nname = "Test"\ndocs_dir = "{sample_config.docs_dir}"\n')
        result = CliRunner().invoke(main, ["search", "Quickstart", "--config", cfg])
        assert result.exit_code == 0
        assert "Quickstart" in result.output

    def test_search_no_results(self, sample_config, monkeypatch):
        monkeypatch.chdir(os.path.dirname(sample_config.docs_dir))
        cfg = os.path.join(os.path.dirname(sample_config.docs_dir), "flydocs.toml")
        with open(cfg, "w") as f:
            f.write(f'[project]\nname = "Test"\ndocs_dir = "{sample_config.docs_dir}"\n')
        result = CliRunner().invoke(main, ["search", "zzzzz", "--config", cfg])
        assert result.exit_code == 0
        assert "No docs matching" in result.output


class TestInitCli:
    def test_init_creates_file(self, tmp_path):
        target = str(tmp_path / "docs" / "new-page.md")
        result = CliRunner().invoke(main, ["init", target])
        assert result.exit_code == 0
        assert "Created" in result.output
        assert os.path.exists(target)
        with open(target) as f:
            content = f.read()
        assert "type: Guide" in content
        assert "title: New Page" in content

    def test_init_custom_type(self, tmp_path):
        target = str(tmp_path / "concept.md")
        result = CliRunner().invoke(main, ["init", target, "--type", "Concept"])
        assert result.exit_code == 0
        with open(target) as f:
            content = f.read()
        assert "type: Concept" in content

    def test_init_refuses_existing(self, tmp_path):
        target = tmp_path / "exists.md"
        target.write_text("already here")
        result = CliRunner().invoke(main, ["init", str(target)])
        assert result.exit_code == 1
        assert "already exists" in result.output


class TestBadgesCli:
    def test_no_badges(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = tmp_path / "flydocs.toml"
        cfg.write_text('[project]\nname = "Test"\n')
        result = CliRunner().invoke(main, ["badges", "--config", str(cfg)])
        assert "No badges configured" in result.output


class TestReadmeCli:
    def test_dry_run(self, sample_config, monkeypatch):
        monkeypatch.chdir(os.path.dirname(sample_config.docs_dir))
        cfg = os.path.join(os.path.dirname(sample_config.docs_dir), "flydocs.toml")
        with open(cfg, "w") as f:
            f.write(f'[project]\nname = "Test"\ndocs_dir = "{sample_config.docs_dir}"\n')
        result = CliRunner().invoke(main, ["readme", "--dry-run", "--config", cfg])
        assert result.exit_code == 0
        assert "Test Project" in result.output


class TestOkfCli:
    def test_okf_preview_not_implemented(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = tmp_path / "flydocs.toml"
        cfg.write_text('[project]\nname = "Test"\n')
        result = CliRunner().invoke(main, ["okf", "preview", "--config", str(cfg)])
        assert result.exit_code == 1
        assert "not yet implemented" in result.output

    def test_okf_init_not_implemented(self):
        result = CliRunner().invoke(main, ["okf", "init"])
        assert result.exit_code == 1
        assert "not yet implemented" in result.output
