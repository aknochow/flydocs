"""Tests for configuration loading."""

from __future__ import annotations

import pytest

from flydocs.config import load_config


class TestLoadConfig:
    def test_no_config_returns_defaults(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = load_config()
        assert config.name == "Documentation"
        assert config.theme.mode == "auto"
        assert config.theme.palette == "flydocs-dark"

    def test_loads_basic_config(self, tmp_path):
        cfg = tmp_path / "flydocs.toml"
        cfg.write_text('[project]\nname = "My Project"\n')
        config = load_config(cfg)
        assert config.name == "My Project"

    def test_type_coercion(self, tmp_path):
        cfg = tmp_path / "flydocs.toml"
        cfg.write_text("[project]\nname = 42\n")
        config = load_config(cfg)
        assert config.name == "42"
        assert isinstance(config.name, str)

    def test_malformed_toml_exits(self, tmp_path):
        cfg = tmp_path / "bad.toml"
        cfg.write_text("this is not valid {{{")
        with pytest.raises(SystemExit, match="invalid TOML"):
            load_config(cfg)

    def test_missing_file_exits(self, tmp_path):
        with pytest.raises(SystemExit, match="not found"):
            load_config(tmp_path / "missing.toml")

    def test_frozen_config(self, tmp_path):
        cfg = tmp_path / "flydocs.toml"
        cfg.write_text('[project]\nname = "Frozen"\n')
        config = load_config(cfg)
        with pytest.raises(AttributeError):
            config.name = "Changed"

    def test_sidebar_config(self, tmp_path):
        cfg = tmp_path / "flydocs.toml"
        cfg.write_text(
            '[project]\nname = "Test"\n'
            "[sidebar]\nexpanded = false\n"
            '[sidebar.overrides]\n"Help" = true\n'
        )
        config = load_config(cfg)
        assert config.sidebar.expanded is False
        assert config.sidebar.overrides["Help"] is True

    def test_readme_config(self, tmp_path):
        cfg = tmp_path / "flydocs.toml"
        cfg.write_text(
            '[project]\nname = "Test"\n'
            "[readme]\nenabled = true\n"
            'output = "OUT.md"\n'
        )
        config = load_config(cfg)
        assert config.readme.enabled is True
        assert config.readme.output == "OUT.md"

    def test_badges_filtered(self, tmp_path):
        cfg = tmp_path / "flydocs.toml"
        cfg.write_text(
            '[project]\nname = "Test"\n'
            '[[badges]]\nid = "v"\nlabel = "v1"\nurl = "https://x"\nimg = "https://i"\n'
            '[[badges]]\nid = ""\nlabel = ""\nurl = ""\nimg = ""\n'
        )
        config = load_config(cfg)
        assert len(config.badges) == 1

    def test_finds_flydocs_toml(self, tmp_path, monkeypatch):
        (tmp_path / "flydocs.toml").write_text('[project]\nname = "Found"\n')
        monkeypatch.chdir(tmp_path)
        config = load_config()
        assert config.name == "Found"

    def test_falls_back_to_docs_toml(self, tmp_path, monkeypatch):
        (tmp_path / "docs.toml").write_text('[project]\nname = "Fallback"\n')
        monkeypatch.chdir(tmp_path)
        config = load_config()
        assert config.name == "Fallback"

    def test_base_path_env_override(self, tmp_path, monkeypatch):
        cfg = tmp_path / "flydocs.toml"
        cfg.write_text('[project]\nname = "Test"\nbase_path = "/config"\n')
        monkeypatch.setenv("DOCS_BASE_PATH", "/env")
        config = load_config(cfg)
        assert config.base_path == "/env"
