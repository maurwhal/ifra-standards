"""Write :class:`Standard` records to CSV, JSON, or XLSX."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable, Iterator
from pathlib import Path

from .models import Standard

__all__ = ["FIELDS", "FIELDS_BY_CAS", "to_records", "write"]

FIELDS = [
    "document_id", "name", "cas_numbers", "cas_list", "type", "type_label",
    "amendment", "publication_date", "pdf_url", "retrieved_at",
]
FIELDS_BY_CAS = [
    "cas", "document_id", "name", "type", "type_label",
    "amendment", "publication_date", "cas_numbers", "pdf_url", "retrieved_at",
]


def to_records(standards: Iterable[Standard], *, explode_cas: bool = False,
               retrieved_at: bool = True) -> Iterator[dict]:
    """Yield one dict per standard, or one dict per (standard, CAS) pair.

    Set ``retrieved_at=False`` to drop the fetch timestamp, which keeps a
    committed dataset's diffs limited to real content changes.
    """
    fields = FIELDS_BY_CAS if explode_cas else FIELDS
    if not retrieved_at:
        fields = [f for f in fields if f != "retrieved_at"]
    for s in standards:
        if explode_cas:
            for cas in s.cas_list or [""]:
                row = s.to_dict(cas_as_list=False)
                row.pop("cas_list", None)
                row["cas"] = cas
                yield {k: row[k] for k in fields}
        else:
            row = s.to_dict(cas_as_list=False)
            yield {k: row[k] for k in fields}


def _fields(explode_cas: bool, retrieved_at: bool) -> list[str]:
    fields = FIELDS_BY_CAS if explode_cas else FIELDS
    return fields if retrieved_at else [f for f in fields if f != "retrieved_at"]


def _write_csv(rows: list[dict], path: Path, fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def _write_json(rows: list[dict], path: Path, *, pretty: bool) -> None:
    path.write_text(
        json.dumps(rows, indent=2 if pretty else None, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_xlsx(rows: list[dict], path: Path, fields: list[str]) -> None:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise SystemExit(
            "XLSX output needs openpyxl: pip install 'ifra-standards[xlsx]'"
        ) from exc
    wb = Workbook()
    ws = wb.active
    ws.title = "IFRA Standards"
    ws.append(fields)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for r in rows:
        ws.append([r.get(f, "") for f in fields])
    ws.freeze_panes = "A2"
    wb.save(path)


def write(standards: Iterable[Standard], path: str | Path, *, fmt: str | None = None,
          explode_cas: bool = False, pretty: bool = True,
          retrieved_at: bool = True) -> Path:
    """Write ``standards`` to ``path``. Format is taken from the suffix unless given."""
    path = Path(path)
    fmt = (fmt or path.suffix.lstrip(".")).lower()
    fields = _fields(explode_cas, retrieved_at)
    rows = list(to_records(standards, explode_cas=explode_cas, retrieved_at=retrieved_at))
    if fmt == "csv":
        _write_csv(rows, path, fields)
    elif fmt == "json":
        _write_json(rows, path, pretty=pretty)
    elif fmt in ("xlsx", "xlsm"):
        _write_xlsx(rows, path, fields)
    else:
        raise ValueError(f"Unknown output format: {fmt!r} (use csv, json or xlsx)")
    return path
