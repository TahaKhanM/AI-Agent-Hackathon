"""The product Gate Console — the per-incident notarised case-file page (WP-CONSOLE).

HARD BOUNDARY (enforced by scripts/check_product_imports.sh + tests/test_product_imports.py):
this package imports NO kernel. Zero imports of ``precedent`` / ``precedent_memory`` /
``precedent_pack`` / ``sim`` / ``console.demo_state``. It is a pure presentation surface — a
server-rendered shell (shared Jinja2 templates + the shared static design system) whose ONLY data
source is the HTTP read/gate endpoints (``/api/*`` + ``/v1/gate/*``), fetched by the browser.

The kernel-backed read/query endpoints those pages consume live OUTSIDE this package, in
``console/read_api.py`` (and ``gate/``), which MAY import the kernel + the pack builder.
"""
from __future__ import annotations

from console.product.router import make_product_router

__all__ = ["make_product_router"]
