"""Minimal CAS Registry Number helpers. Standard library only.

A CAS number looks like ``127-91-3``: two to seven digits, a hyphen, two digits,
a hyphen, and a single check digit. The check digit is a weighted sum of the
other digits, which lets us tell a real CAS number from a lookalike string of
digits.
"""

from __future__ import annotations

import re

__all__ = ["extract_cas", "is_valid_cas", "split_cas_field"]

_CAS_RE = re.compile(r"\b(\d{2,7}-\d{2}-\d)\b")
_CAS_FULL_RE = re.compile(r"^(\d{2,7})-(\d{2})-(\d)$")


def is_valid_cas(cas: str) -> bool:
    """Return True if ``cas`` is well formed and its check digit is correct.

    >>> is_valid_cas("50-00-0")   # formaldehyde
    True
    >>> is_valid_cas("50-00-1")
    False
    """
    m = _CAS_FULL_RE.match((cas or "").strip())
    if not m:
        return False
    body = m.group(1) + m.group(2)
    check = int(m.group(3))
    total = sum(i * int(d) for i, d in enumerate(reversed(body), start=1))
    return total % 10 == check


def extract_cas(text: str, *, validate: bool = True) -> list[str]:
    """Pull CAS numbers out of a free-text string.

    Order is preserved and duplicates are dropped. With ``validate=True``
    (the default) only numbers with a correct check digit are returned, so
    things like RIFM ids or survey numbers are ignored.

    >>> extract_cas("127-91-3 (RIFM ID: 690)")
    ['127-91-3']
    """
    out: dict[str, None] = {}
    for cand in _CAS_RE.findall(text or ""):
        if validate and not is_valid_cas(cand):
            continue
        out.setdefault(cand, None)
    return list(out)


def split_cas_field(field: str, *, validate: bool = True) -> list[str]:
    """Split an IFRA CAS cell into individual numbers.

    IFRA lists several CAS numbers in one cell separated by spaces, semicolons
    or commas (``"144020-22-4 28371-99-5"``). This is just :func:`extract_cas`
    under a clearer name for that use.
    """
    return extract_cas(field, validate=validate)
