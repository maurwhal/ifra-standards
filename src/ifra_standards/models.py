"""The :class:`Standard` record."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from .cas import split_cas_field

__all__ = ["TYPE_LABELS", "Standard"]

#: IFRA Standard types. A blank type is used for some older group entries.
TYPE_LABELS = {
    "R": "Restriction",
    "P": "Prohibition",
    "S": "Specification",
    "": "Unspecified",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class Standard:
    """One published IFRA Standard, as listed in the Standards Library."""

    document_id: int
    name: str
    #: CAS number(s) exactly as IFRA prints them (may hold several, space separated)
    cas_numbers: str
    #: ``R`` / ``P`` / ``S`` / ``""``
    type: str
    #: amendment the standard was last issued or revised in, as a string
    amendment: str
    #: publication date, ``"YYYY-MM"``
    publication_date: str
    #: direct link to the standard PDF
    pdf_url: str
    #: UTC timestamp of when this record was fetched
    retrieved_at: str = field(default_factory=_now)

    @property
    def cas_list(self) -> list[str]:
        """The CAS number(s) split into a list, check-digit validated."""
        return split_cas_field(self.cas_numbers)

    @property
    def type_label(self) -> str:
        return TYPE_LABELS.get(self.type, self.type)

    def to_dict(self, *, cas_as_list: bool = True) -> dict:
        d = asdict(self)
        d["type_label"] = self.type_label
        d["cas_list"] = self.cas_list if cas_as_list else "; ".join(self.cas_list)
        return d
