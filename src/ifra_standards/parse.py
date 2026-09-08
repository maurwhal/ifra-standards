"""Turn a rendered library-table HTML page into :class:`Standard` records.

Every table row carries a ``data-layer`` attribute holding a small JSON object
with the same fields the visible cells show. We read that, and take the PDF link
from the row's download button.
"""

from __future__ import annotations

import json
import re
from html import unescape

from .models import Standard

__all__ = ["parse_standards"]

_ROW_RE = re.compile(r"<tr\b.*?</tr>", re.S)
_DATALAYER_RE = re.compile(
    r'data-layer="(\{&quot;event&quot;:&quot;download&quot;.*?\})"', re.S
)
_HREF_RE = re.compile(r'href="(https://[^"]+/IFRA_STD_[^"]+\.pdf)"')


def _clean_title(name: str) -> str:
    n = (name or "").strip()
    if len(n) >= 2 and n[0] == '"' and n[-1] == '"':
        n = n[1:-1].strip()
    return n


def parse_standards(html: str) -> list[Standard]:
    """Parse every standard from a rendered library-table HTML page.

    Raises :class:`ValueError` if nothing parses, which usually means IFRA
    changed the table markup.
    """
    out: list[Standard] = []
    seen: set[int] = set()
    for row in _ROW_RE.findall(html):
        dl = _DATALAYER_RE.search(row)
        if not dl:
            continue
        rec = json.loads(unescape(dl.group(1)))
        if rec.get("document_type") not in (None, "standards"):
            continue
        try:
            doc_id = int(rec["document_id"])
        except (KeyError, TypeError, ValueError):
            continue
        if doc_id in seen:
            continue
        seen.add(doc_id)
        href = _HREF_RE.search(row)
        out.append(
            Standard(
                document_id=doc_id,
                name=_clean_title(rec.get("document_name", "")),
                cas_numbers=(rec.get("cas_number") or "").strip(),
                type=(rec.get("type") or "").strip(),
                amendment=str(rec.get("amendment") or "").strip(),
                publication_date=(rec.get("publication_date") or "").strip(),
                pdf_url=href.group(1) if href else "",
            )
        )
    if not out:
        raise ValueError(
            "No standards found in the HTML. The Standards Library table markup "
            "may have changed."
        )
    out.sort(key=lambda s: s.name.lower())
    return out
