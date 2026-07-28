"""Local development server."""

from __future__ import annotations

import dataclasses
import functools
import http.server

from flydocs.builder import build_site
from flydocs.config import Config


def preview(config: Config, port: int = 8000) -> None:
    """Build and preview the documentation site locally."""
    local_config = dataclasses.replace(config, base_path="")

    build_site(local_config, clean=True)

    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=config.site_dir,
    )
    server = http.server.HTTPServer(("127.0.0.1", port), handler)
    print(f"\nServing at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped")
