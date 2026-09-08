"""Download the standard PDFs referenced by an export."""

from __future__ import annotations

import time
import urllib.request
from collections.abc import Iterable
from pathlib import Path

from .client import USER_AGENT, IFRAError
from .models import Standard

__all__ = ["download_pdfs"]


def download_pdfs(standards: Iterable[Standard], out_dir: str | Path, *,
                  overwrite: bool = False, delay: float = 1.0,
                  timeout: float = 120.0) -> list[Path]:
    """Save each standard's PDF into ``out_dir``. Returns the paths written.

    A ``delay`` (seconds) is applied between downloads to stay polite.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    items = [s for s in standards if s.pdf_url]
    for idx, s in enumerate(items):
        dest = out / s.pdf_url.rsplit("/", 1)[-1]
        if dest.exists() and not overwrite:
            written.append(dest)
            continue
        req = urllib.request.Request(s.pdf_url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                dest.write_bytes(resp.read())
        except Exception as exc:
            raise IFRAError(f"Failed to download {s.pdf_url}: {exc}") from exc
        written.append(dest)
        if delay and idx < len(items) - 1:
            time.sleep(delay)
    return written
