"""Tests for reading a Standard PDF's fields.

These run against made-up text fixtures in the real IFRA Standard layout
(tests/fixtures/detail_text_*.txt), not against any real IFRA document, so the
suite stays network-free and does not redistribute IFRA content.
"""

import ifra_standards.pdf_detail as pdf_detail
from ifra_standards.models import Standard
from ifra_standards.pdf_detail import (
    CATEGORIES,
    detail_record,
    fetch_all_details,
    parse_detail_text,
)


def test_restriction_fields(restriction_detail_text):
    d = parse_detail_text(restriction_detail_text, pdf_url="https://example/x.pdf")
    assert d.name == "Example Fragrance Ketone"
    assert d.cas_numbers == ["999999-11-1", "888888-22-2"] or set(d.cas_numbers) <= {
        "999999-11-1", "888888-22-2",
    }
    assert d.recommendation == "RESTRICTION"
    assert d.amendment == "51"
    assert d.publication_year == "2023"
    assert d.pdf_url == "https://example/x.pdf"


def test_previous_publications_ignores_the_word_previously(restriction_detail_text):
    # "previously" appears in the CAS-scope note before the real "Previous
    # Publications" label; make sure that does not get matched as the label.
    d = parse_detail_text(restriction_detail_text)
    assert d.previous_publications == ["2011", "2005"]
    assert d.publication_year not in d.previous_publications


def test_implementation_dates(restriction_detail_text):
    d = parse_detail_text(restriction_detail_text)
    assert d.implementation_new_creation == "January 1, 2024"
    assert d.implementation_existing_creation == "January 1, 2025"


def test_all_categories_read(restriction_detail_text):
    d = parse_detail_text(restriction_detail_text)
    assert set(CATEGORIES) == set(d.categories)
    assert all(d.categories[c] for c in CATEGORIES)
    assert d.categories["1"] == "0.001 %"
    assert d.categories["12"] == "No Restriction"
    assert d.categories["5D"] == "0.20 %"


def test_intrinsic_property_stops_before_rifm_summaries(restriction_detail_text):
    d = parse_detail_text(restriction_detail_text)
    assert d.intrinsic_property_driving_risk_management == (
        "DERMAL SENSITIZATION AND SYSTEMIC TOXICITY"
    )
    assert "RIFM" not in d.intrinsic_property_driving_risk_management


def test_prohibition_specification_combo(prohibition_specification_detail_text):
    d = parse_detail_text(prohibition_specification_detail_text)
    assert d.recommendation == "PROHIBITION / SPECIFICATION"
    assert d.prohibition_text == "Example Solvent should not be used as a fragrance ingredient"
    assert "1 ppm" in d.specification_text
    assert all(v is None for v in d.categories.values())
    assert d.intrinsic_property_driving_risk_management == "CARCINOGENICITY"
    assert d.previous_publications == ["1990"]


def _standard(**kw):
    base = {
        "document_id": 1, "name": "Example Solvent", "cas_numbers": "111-11-1",
        "type": "P", "amendment": "38", "publication_date": "2004-01",
        "pdf_url": "https://example/x.pdf",
    }
    base.update(kw)
    return Standard(**base)


def test_detail_record_merges_list_and_pdf_fields(prohibition_specification_detail_text):
    s = _standard()
    d = parse_detail_text(prohibition_specification_detail_text, pdf_url=s.pdf_url)
    row = detail_record(s, d)
    assert row["name"] == "Example Solvent"  # from the list, not re-derived from the PDF
    assert row["cas_numbers"] == "111-11-1"
    assert row["recommendation"] == "PROHIBITION / SPECIFICATION"
    assert row["category_1"] == ""
    assert "should not be used" in row["prohibition_text"]
    assert row["error"] == ""


def test_detail_record_with_error_has_blank_pdf_fields():
    s = _standard()
    row = detail_record(s, None, error="URLError: timed out")
    assert row["error"] == "URLError: timed out"
    assert row["recommendation"] == ""
    assert row["category_1"] == ""
    assert row["name"] == "Example Solvent"


def test_fetch_all_details_reads_from_pdf_dir_without_network(
    tmp_path, monkeypatch, restriction_detail_text
):
    # A pdf_dir hit should never call the network. Fake the PDF bytes and
    # monkeypatch extract_text so this test needs no real PDF file.
    (tmp_path / "x.pdf").write_bytes(b"not a real pdf")
    monkeypatch.setattr(pdf_detail, "extract_text", lambda data: restriction_detail_text)

    def _boom(*a, **k):
        raise AssertionError("should not hit the network when the PDF is already in pdf_dir")

    monkeypatch.setattr(pdf_detail.urllib.request, "urlopen", _boom)

    s = _standard(name="Example Fragrance Ketone", pdf_url="https://example/x.pdf")
    rows = list(fetch_all_details([s], pdf_dir=tmp_path, delay=0))
    assert len(rows) == 1
    assert rows[0]["error"] == ""
    assert rows[0]["category_1"] == "0.001 %"


def test_fetch_all_details_records_a_failure_without_stopping(tmp_path, monkeypatch):
    def _boom(*a, **k):
        raise OSError("network is down")

    monkeypatch.setattr(pdf_detail.urllib.request, "urlopen", _boom)

    s1 = _standard(document_id=1, pdf_url="https://example/one.pdf")
    s2 = _standard(document_id=2, pdf_url="https://example/two.pdf")
    rows = list(fetch_all_details([s1, s2], delay=0))
    assert len(rows) == 2
    assert all("network is down" in r["error"] for r in rows)
