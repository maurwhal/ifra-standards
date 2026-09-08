"""Fetch raw HTML from the IFRA Standards Library.

The library page (https://ifrafragrance.org/standards-library) renders its table
through a Craft CMS "Sprig" component. A single request to that component's
render endpoint, with a high ``limit``, returns every standard in one HTML
table.

The endpoint needs a signed ``sprig:config`` token that is embedded in the
library page and rotates whenever IFRA redeploys the site, so we scrape a fresh
one on each run.

Standard library only, no third-party dependencies.
"""

from __future__ import annotations

import gzip
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html import unescape

from .__about__ import __version__

__all__ = ["BASE", "IFRAError", "discover_config", "fetch_raw_html"]

BASE = "https://ifrafragrance.org"
LIBRARY_PATH = "/standards-library"
RENDER_PATH = "/index.php/actions/sprig-core/components/render"
USER_AGENT = (
    f"ifra-standards/{__version__} "
    "(+https://github.com/maurwhal/ifra-standards)"
)

# the one hx-vals attribute that carries the standards-library component config
_CONFIG_RE = re.compile(r'hx-vals="([^"]*sprig:config[^"]*standards-library[^"]*)"')


class IFRAError(RuntimeError):
    """Raised when the site cannot be reached or its layout has changed."""


def _get(url: str, *, timeout: float, retries: int, backoff: float) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Encoding": "gzip",
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return raw.decode("utf-8", "replace")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:  # noqa: PERF203
            last = exc
            if attempt < retries:
                time.sleep(backoff * (2**attempt))
    raise IFRAError(f"GET {url} failed after {retries + 1} attempt(s): {last}")


def discover_config(*, timeout: float = 30.0, retries: int = 3,
                    backoff: float = 1.0) -> str:
    """Scrape the current signed ``sprig:config`` token from the library page.

    The token is HMAC-signed over its exact string (including a backslash before
    the template slash), so it is returned verbatim and must not be reformatted.
    """
    html = _get(BASE + LIBRARY_PATH, timeout=timeout, retries=retries, backoff=backoff)
    m = _CONFIG_RE.search(html)
    if not m:
        raise IFRAError(
            "Could not find the sprig:config token on the standards-library "
            "page. IFRA may have changed the page. Please open an issue at "
            "https://github.com/maurwhal/ifra-standards/issues"
        )
    payload = json.loads(unescape(m.group(1)))
    return payload["sprig:config"]


def fetch_raw_html(*, config: str | None = None, limit: int = 2000,
                   timeout: float = 60.0, retries: int = 3, backoff: float = 1.0,
                   polite_delay: float = 0.5) -> str:
    """Return the full rendered standards table as HTML.

    Makes two requests if ``config`` is not supplied (one to read the token, one
    to render the table), otherwise one.
    """
    if config is None:
        config = discover_config(timeout=timeout, retries=retries, backoff=backoff)
        if polite_delay:
            time.sleep(polite_delay)
    query = urllib.parse.urlencode({"sprig:config": config, "limit": str(limit)})
    html = _get(
        f"{BASE}{RENDER_PATH}?{query}",
        timeout=timeout, retries=retries, backoff=backoff,
    )
    if "c-pagination" in html:
        raise IFRAError(
            f"The response was paginated at limit={limit}; the library has more "
            "standards than expected. Re-run with a higher --limit."
        )
    return html
