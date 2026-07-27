"""Tests for the preview server."""

from __future__ import annotations

import os
import threading
import urllib.request

from flydocs.server import preview


class TestPreview:
    def test_preview_builds_and_serves(self, sample_config, monkeypatch):
        monkeypatch.chdir(os.path.dirname(sample_config.docs_dir))
        port = 18933
        error_holder = []

        def run_preview():
            try:
                preview(sample_config, port=port)
            except (OSError, SystemExit) as e:
                error_holder.append(e)

        t = threading.Thread(target=run_preview, daemon=True)
        t.start()

        import time

        for _ in range(20):
            time.sleep(0.25)
            try:
                resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/")
                break
            except (ConnectionRefusedError, urllib.error.URLError):
                continue
        else:
            if error_holder:
                raise error_holder[0]
            raise AssertionError("Server did not start within 5 seconds")

        assert resp.status == 200
        html = resp.read().decode()
        assert "Test Project" in html
        assert "pf-v6-c-nav" in html
        assert "flydocs.css" in html

    def test_preview_clears_base_path(self, sample_config, monkeypatch):
        monkeypatch.chdir(os.path.dirname(sample_config.docs_dir))
        from flydocs.builder import build_site
        from flydocs.config import Config

        local_config = Config(
            name=sample_config.name,
            docs_dir=sample_config.docs_dir,
            site_dir=sample_config.site_dir,
            base_path="",
            nav=sample_config.nav,
        )
        build_site(local_config)
        with open(os.path.join(sample_config.site_dir, "index.html")) as f:
            html = f.read()
        assert 'href="/flydocs/' not in html
