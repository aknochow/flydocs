"""Tests for CLI search."""

from __future__ import annotations

from flydocs.search import search


class TestSearch:
    def test_finds_by_title(self, sample_config, capsys):
        search("Quickstart", sample_config)
        output = capsys.readouterr().out
        assert "Quickstart" in output
        assert "[Guide]" in output

    def test_finds_by_description(self, sample_config, capsys):
        search("test project", sample_config)
        output = capsys.readouterr().out
        assert "Test Project" in output

    def test_no_results(self, sample_config, capsys):
        search("zzzznonexistent", sample_config)
        output = capsys.readouterr().out
        assert "No docs matching" in output

    def test_case_insensitive(self, sample_config, capsys):
        search("quickstart", sample_config)
        output = capsys.readouterr().out
        assert "Quickstart" in output
