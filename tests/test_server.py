"""Tests for the preview server."""

from __future__ import annotations

import os
import threading
import urllib.request



class TestPreview:
    def test_preview_builds_and_serves(self, sample_config, monkeypatch):
        monkeypatch.chdir(os.path.dirname(sample_config.docs_dir))
        port = 18933
        server_started = threading.Event()


        def patched_preview(config, port):
            import functools
            import http.server

            from flydocs.builder import build_site
            from flydocs.config import Config

            local_config = Config(
                name=config.name,
                url=config.url,
                description=config.description,
                docs_dir=config.docs_dir,
                site_dir=config.site_dir,
                base_path="",
                theme=config.theme,
                sidebar=config.sidebar,
                readme=config.readme,
                badges=config.badges,
                nav=config.nav,
            )
            build_site(local_config, clean=True)

            handler = functools.partial(
                http.server.SimpleHTTPRequestHandler,
                directory=config.site_dir,
            )
            srv = http.server.HTTPServer(("127.0.0.1", port), handler)
            server_started.set()
            srv.handle_request()
            srv.server_close()

        t = threading.Thread(
            target=patched_preview,
            args=(sample_config, port),
            daemon=True,
        )
        t.start()
        server_started.wait(timeout=10)

        resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/")
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
            url=sample_config.url,
            description=sample_config.description,
            docs_dir=sample_config.docs_dir,
            site_dir=sample_config.site_dir,
            base_path="",
            theme=sample_config.theme,
            sidebar=sample_config.sidebar,
            readme=sample_config.readme,
            badges=sample_config.badges,
            nav=sample_config.nav,
        )
        build_site(local_config)
        with open(os.path.join(sample_config.site_dir, "index.html")) as f:
            html = f.read()
        assert 'href="/flydocs/' not in html
        assert 'href="/"' in html or 'href="/guides/' in html
