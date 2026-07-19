"""Tests for README generation."""

from __future__ import annotations

from flydocs.readme import _rewrite_doc_links, generate_readme


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

    def test_includes_badges(self):
        from flydocs.config import Badge, Config

        docs = "/tmp/flydocs-test-readme-badges"
        import os

        os.makedirs(docs, exist_ok=True)
        with open(os.path.join(docs, "index.md"), "w") as f:
            f.write("---\ntype: Guide\ntitle: T\ndescription: D\n---\n# T\n")
        try:
            config = Config(
                name="T",
                docs_dir=docs,
                badges=(Badge(id="v", label="v1", url="https://x", img="https://i"),),
            )
            content = generate_readme(config)
            assert "[![v1]" in content
        finally:
            import shutil

            shutil.rmtree(docs)
