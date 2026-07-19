"""Local development server."""

from __future__ import annotations

import functools
import http.server

from flydocs.builder import build_site
from flydocs.config import Config


def preview(config: Config, port: int = 8000) -> None:
    """Build and preview the documentation site locally."""
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
    server = http.server.HTTPServer(("127.0.0.1", port), handler)
    print(f"\nServing at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped")
