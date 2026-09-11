"""Read one IFRA Standard PDF: the Maximum Acceptable Concentrations and the
other fields inside it, not just the summary row from the library table.

Every Standard PDF uses the same labeled layout (CAS-No., Synonyms, History,
Implementation dates, Recommendation, then either a Maximum Acceptable
Concentrations table, a Prohibition, or a Specification, then Contributions
from other sources, Intrinsic property driving risk management, and
References). This module reads the PDF's text and pulls those fields out.

Needs pypdf, an optional extra (``pip install "ifra-standards[pdf]"``).
"""

from __future__ import annotations

import re
import time
import urllib.request
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass
from pathlib import Path

from .cas import extract_cas

__all__ = [
    "CATEGORIES",
    "StandardDetail",
    "detail_record",
    "extract_text",
    "fetch_all_details",
    "fetch_standard_detail",
    "parse_detail_text",
]

#: Every category the Maximum Acceptable Concentrations table can list, in the
#: order IFRA prints them.
CATEGORIES = (
    "1", "2", "3", "4", "5A", "5B", "5C", "5D", "6",
    "7A", "7B", "8", "9", "10A", "10B", "11A", "11B", "12",
)

_CATEGORY_RE = re.compile(
    r"Category\s+(\d{1,2}[A-D]?)\s+(No\s+Restriction|[\d.,]+\s*%)", re.IGNORECASE
)


@dataclass
class StandardDetail:
    """The fields read out of one Standard PDF."""

    name: str | None
    cas_numbers: list[str]
    recommendation: str | None
    amendment: str | None
    publication_year: str | None
    previous_publications: list[str]
    implementation_new_creation: str | None
    implementation_existing_creation: str | None
    categories: dict[str, str | None]
    prohibition_text: str | None
    specification_text: str | None
    contributions_from_other_sources: str | None
    intrinsic_property_driving_risk_management: str | None
    pdf_url: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# Every page repeats a running header ("Amendment 44 IFRA STANDARD <title>
# 2009 (Amendment 44) 2/2 IFRA STANDARD"). When a field's text runs across a
# page break, that header lands in the middle of it; strip it back out.
_PAGE_BANNER_RE = re.compile(
    r"Amendment\s+\d+\s+IFRA\s+STANDARD\s+.{0,200}?\(Amendment\s+\d+\)\s+\d+/\d+\s+IFRA\s+STANDARD",
    re.S,
)


def _clean(s: str | None) -> str | None:
    if s is None:
        return None
    s = re.sub(r"\s+", " ", s).strip(" \n\t.:")
    s = _PAGE_BANNER_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip(" \n\t.:")
    return s or None


def _between(text: str, start: str, end_labels: tuple[str, ...]) -> str | None:
    """Text from just after ``start`` up to whichever ``end_labels`` comes first."""
    m = re.search(re.escape(start), text, re.IGNORECASE)
    if not m:
        return None
    tail = text[m.end():]
    end = len(tail)
    for label in end_labels:
        m2 = re.search(re.escape(label), tail, re.IGNORECASE)
        if m2 and m2.start() < end:
            end = m2.start()
    return tail[:end]


def extract_text(pdf_bytes: bytes) -> str:
    """Read every page of a Standard PDF as plain text."""
    try:
        import pypdf
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise SystemExit(
            'Reading a Standard PDF needs pypdf: pip install "ifra-standards[pdf]"'
        ) from exc
    from io import BytesIO

    reader = pypdf.PdfReader(BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def parse_detail_text(text: str, *, pdf_url: str = "") -> StandardDetail:
    """Pull the fields out of a Standard PDF's extracted text."""
    name_m = re.search(r"STANDARD\s*(.+?)\s*\d{4}\s*\(Amendment", text, re.S)
    name = _clean(name_m.group(1)) if name_m else None

    cas_block = _between(text, "CAS-No.:", ("The scope of this Standard", "Synonyms:")) or ""
    cas_numbers = extract_cas(cas_block)

    pub_m = re.search(r"Publication date:\s*(\d{4})\s*\(Amendment\s*(\d+)\)", text, re.I)
    publication_year = pub_m.group(1) if pub_m else None
    amendment = pub_m.group(2) if pub_m else None

    # \b before "Previous" matters: without it this also matches inside "previously",
    # which shows up in some CAS-scope notes earlier in the document.
    prev_m = re.search(
        r"\bPrevious\s+Publications:?\s*(.*?)(?=Implementation|For new creation)",
        text, re.S | re.I,
    )
    prev_block = prev_m.group(1) if prev_m else ""
    previous_publications = [
        y for y in re.findall(r"\b(?:19|20)\d{2}\b", prev_block) if y != publication_year
    ]

    new_m = re.search(r"For new creation\*?:\s*(.+?)(?:\n|For existing)", text, re.I)
    existing_m = re.search(r"For existing creation\*?:\s*(.+?)\n", text, re.I)

    rec_m = re.search(r"RECOMMENDATION:\s*(.+?)\n", text, re.I)
    recommendation = _clean(rec_m.group(1)) if rec_m else None
    rec_upper = (recommendation or "").upper()

    categories: dict[str, str | None] = dict.fromkeys(CATEGORIES)
    if "RESTRICTION" in rec_upper:
        mac_block = _between(
            text, "MAXIMUM ACCEPTABLE CONCENTRATIONS",
            ("FLAVOR REQUIREMENTS:", "CONTRIBUTIONS FROM OTHER SOURCES:",
             "INTRINSIC PROPERTY DRIVING RISK"),
        ) or ""
        for cat, value in _CATEGORY_RE.findall(mac_block):
            cat = cat.upper()
            if cat in categories:
                categories[cat] = _clean(value)

    prohibition_text = None
    if "PROHIBITION" in rec_upper:
        prohibition_text = _clean(_between(
            text, "FRAGRANCE INGREDIENT PROHIBITION:",
            ("FRAGRANCE INGREDIENT SPECIFICATION:", "FLAVOR REQUIREMENTS:",
             "CONTRIBUTIONS FROM OTHER SOURCES:", "INTRINSIC PROPERTY DRIVING RISK"),
        ))

    specification_text = None
    if "SPECIFICATION" in rec_upper:
        specification_text = _clean(_between(
            text, "FRAGRANCE INGREDIENT SPECIFICATION:",
            ("FLAVOR REQUIREMENTS:", "CONTRIBUTIONS FROM OTHER SOURCES:",
             "INTRINSIC PROPERTY DRIVING RISK"),
        ))

    contributions = _clean(_between(
        text, "CONTRIBUTIONS FROM OTHER SOURCES:",
        ("INTRINSIC PROPERTY DRIVING RISK",),
    ))
    intrinsic_property = _clean(_between(
        text, "INTRINSIC PROPERTY DRIVING RISK",
        ("RIFM SUMMAR", "EXPERT PANEL FOR FRAGRANCE SAFETY", "REFERENCES:"),
    ))
    if intrinsic_property:
        intrinsic_property = re.sub(r"^MANAGEMENT:?\s*", "", intrinsic_property, flags=re.I)

    return StandardDetail(
        name=name,
        cas_numbers=cas_numbers,
        recommendation=recommendation,
        amendment=amendment,
        publication_year=publication_year,
        previous_publications=previous_publications,
        implementation_new_creation=_clean(new_m.group(1)) if new_m else None,
        implementation_existing_creation=_clean(existing_m.group(1)) if existing_m else None,
        categories=categories,
        prohibition_text=prohibition_text,
        specification_text=specification_text,
        contributions_from_other_sources=contributions,
        intrinsic_property_driving_risk_management=intrinsic_property,
        pdf_url=pdf_url,
    )


def fetch_standard_detail(source: str, *, timeout: float = 60.0) -> StandardDetail:
    """Read one Standard's details from a PDF URL or a local file path."""
    if re.match(r"^https?://", source):
        req = urllib.request.Request(source, headers={"User-Agent": "ifra-standards"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        url = source
    else:
        data = Path(source).read_bytes()
        url = ""
    text = extract_text(data)
    return parse_detail_text(text, pdf_url=url)


#: Column order for a flattened detail row (see ``detail_record``).
DETAIL_FIELDS = (
    "document_id", "name", "cas_numbers", "type", "type_label", "amendment",
    "publication_date", "recommendation",
    *(f"category_{c.lower()}" for c in CATEGORIES),
    "prohibition_text", "specification_text",
    "contributions_from_other_sources",
    "intrinsic_property_driving_risk_management", "pdf_url", "error",
)


def detail_record(standard, detail: StandardDetail | None, error: str = "") -> dict:
    """Flatten a library-list :class:`~ifra_standards.models.Standard` plus the
    :class:`StandardDetail` read from its PDF into one CSV-ready row.

    The name, CAS number(s), type, and dates come from the library list, which
    is more consistent than trying to re-derive them from the PDF text. The
    category limits and the other PDF-only fields come from ``detail``.
    """
    row = {
        "document_id": standard.document_id,
        "name": standard.name,
        "cas_numbers": standard.cas_numbers,
        "type": standard.type,
        "type_label": standard.type_label,
        "amendment": standard.amendment,
        "publication_date": standard.publication_date,
        "pdf_url": standard.pdf_url,
        "error": error,
    }
    for field_name in DETAIL_FIELDS:
        row.setdefault(field_name, "")
    if detail is not None:
        row["recommendation"] = detail.recommendation or ""
        for cat in CATEGORIES:
            row[f"category_{cat.lower()}"] = detail.categories.get(cat) or ""
        row["prohibition_text"] = detail.prohibition_text or ""
        row["specification_text"] = detail.specification_text or ""
        row["contributions_from_other_sources"] = detail.contributions_from_other_sources or ""
        row["intrinsic_property_driving_risk_management"] = (
            detail.intrinsic_property_driving_risk_management or ""
        )
    return {k: row.get(k, "") for k in DETAIL_FIELDS}


def fetch_all_details(
    standards: Iterable, *, pdf_dir: str | Path | None = None,
    delay: float = 1.0, timeout: float = 60.0,
) -> Iterator[dict]:
    """Read every Standard's PDF and yield one flattened row per Standard.

    Reads from ``pdf_dir`` (as saved by ``ifra-standards pdfs``) when the file
    is already there, and only downloads what is missing. One Standard's PDF
    failing to download or parse does not stop the rest; it is recorded in
    that row's "error" column instead.
    """
    pdf_dir = Path(pdf_dir) if pdf_dir else None
    standards = list(standards)
    for i, s in enumerate(standards):
        error = ""
        detail = None
        try:
            local = pdf_dir / s.pdf_url.rsplit("/", 1)[-1] if pdf_dir else None
            if local and local.exists():
                data = local.read_bytes()
            else:
                req = urllib.request.Request(s.pdf_url, headers={"User-Agent": "ifra-standards"})
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = resp.read()
                if delay and i < len(standards) - 1:
                    time.sleep(delay)
            detail = parse_detail_text(extract_text(data), pdf_url=s.pdf_url)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        yield detail_record(s, detail, error)
