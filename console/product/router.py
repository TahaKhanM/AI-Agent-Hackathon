"""The /console page router — the notarised case-file console (WP-CONSOLE).

Kernel-free by construction (see the package docstring + the CI import guard). This module only
renders the shared Jinja2 template; ALL data is fetched by the browser from the HTTP read/gate
endpoints. It imports fastapi + jinja2 + pathlib — nothing from precedent*/sim/console.demo_state.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# The shared design-system templates (console/templates/**). We render the product page from the
# SAME directory the demo console uses, so it inherits console/static/css/precedent.css.
_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
_templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


def make_product_router() -> APIRouter:
    """Build the /console router — a single server-rendered shell page."""
    router = APIRouter(tags=["console-product"])

    @router.get("/console", response_class=HTMLResponse,
                summary="The per-incident notarised case-file console")
    def case_file_console(request: Request) -> HTMLResponse:
        # Modern TemplateResponse signature (request=, name=) — the shell is static; the three
        # panels hydrate over HTTP from /api/* + /v1/gate/*.
        return _templates.TemplateResponse(request=request, name="product/case_file.html")

    return router
