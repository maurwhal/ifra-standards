"""ifra-standards: make a spreadsheet of every published IFRA Standard.

    >>> from ifra_standards import fetch_standards
    >>> standards = fetch_standards()
    >>> len(standards)
    263

This reads the public IFRA Standards Library page and copies the list. It does
not log in and does not reach anything that is not already public. It does not
contain or redistribute any IFRA documents. Not affiliated with or endorsed by
IFRA.
"""

from __future__ import annotations

from .__about__ import __version__
from .client import BASE, IFRAError, discover_config, fetch_raw_html
from .diff import diff_standards, format_markdown, load_export
from .export import to_records, write
from .models import TYPE_LABELS, Standard
from .parse import parse_standards
from .pdf_detail import CATEGORIES, StandardDetail, fetch_all_details, fetch_standard_detail
from .pdfs import download_pdfs

__all__ = [
    "BASE",
    "CATEGORIES",
    "TYPE_LABELS",
    "IFRAError",
    "Standard",
    "StandardDetail",
    "__version__",
    "diff_standards",
    "discover_config",
    "download_pdfs",
    "fetch_all_details",
    "fetch_raw_html",
    "fetch_standard_detail",
    "fetch_standards",
    "format_markdown",
    "load_export",
    "parse_standards",
    "to_records",
    "write",
]


def fetch_standards(*, limit: int = 2000, config: str | None = None, **kwargs) -> list[Standard]:
    """Fetch and parse every published IFRA Standard.

    Makes one or two HTTP requests to ifrafragrance.org. Extra keyword arguments
    (``timeout``, ``retries``, ``backoff``, ``polite_delay``) are passed to
    :func:`fetch_raw_html`.
    """
    html = fetch_raw_html(limit=limit, config=config, **kwargs)
    return parse_standards(html)
