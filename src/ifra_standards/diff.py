"""Compare two exports and describe what changed between them."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from .models import Standard

__all__ = ["diff_standards", "format_markdown", "load_export"]

_TRACKED = ("name", "cas_numbers", "type", "amendment", "publication_date", "pdf_url")


def load_export(path: str | Path) -> list[Standard]:
    """Load a JSON export (as written by :func:`ifra_standards.export.write`)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a JSON list of standards")
    keep = {f.name for f in Standard.__dataclass_fields__.values()}
    return [Standard(**{k: v for k, v in row.items() if k in keep}) for row in data]


def diff_standards(old: Iterable[Standard], new: Iterable[Standard]) -> dict:
    """Return ``{"added": [...], "removed": [...], "changed": [(std, {field: (old, new)})]}``."""
    o = {s.document_id: s for s in old}
    n = {s.document_id: s for s in new}
    added = [n[i] for i in sorted(n.keys() - o.keys())]
    removed = [o[i] for i in sorted(o.keys() - n.keys())]
    changed = []
    for i in sorted(o.keys() & n.keys()):
        deltas = {
            f: (getattr(o[i], f), getattr(n[i], f))
            for f in _TRACKED
            if getattr(o[i], f) != getattr(n[i], f)
        }
        if deltas:
            changed.append((n[i], deltas))
    return {"added": added, "removed": removed, "changed": changed}


def format_markdown(d: dict) -> str:
    """Render a diff as a short Markdown summary."""
    lines: list[str] = []
    a, r, c = d["added"], d["removed"], d["changed"]
    if not (a or r or c):
        return "No changes.\n"
    lines.append(f"**{len(a)} added, {len(r)} removed, {len(c)} changed.**\n")
    if a:
        lines.append("### Added\n")
        lines.extend(
            f"- {s.name} ({s.cas_numbers or 'no CAS'}) - "
            f"{s.type_label}, {s.amendment} Amendment"
            for s in a
        )
        lines.append("")
    if r:
        lines.append("### Removed\n")
        lines.extend(f"- {s.name} ({s.cas_numbers or 'no CAS'})" for s in r)
        lines.append("")
    if c:
        lines.append("### Changed\n")
        for s, deltas in c:
            lines.append(f"- **{s.name}**")
            for fld, (before, after) in deltas.items():
                lines.append(f"  - {fld}: `{before}` -> `{after}`")
        lines.append("")
    return "\n".join(lines) + "\n"
