import pytest

from ifra_standards.parse import parse_standards


def test_parses_all_sample_rows(sample_html):
    standards = parse_standards(sample_html)
    assert len(standards) == 4
    assert len({s.document_id for s in standards}) == 4


def test_fields_and_title_quote_stripping(sample_html):
    by_id = {s.document_id: s for s in parse_standards(sample_html)}
    s = by_id[16999]
    expected = (
        "Acetic acid, anhydride, reaction products with "
        "1,5,10-Trimethyl-1,5,9-cyclododecatriene"
    )
    assert s.name == expected
    assert s.type == "R"
    assert s.type_label == "Restriction"
    assert s.amendment == "49"
    assert s.publication_date == "2020-01"
    assert s.pdf_url.endswith("/IFRA_STD_001.pdf")


def test_multi_cas_split(sample_html):
    by_id = {s.document_id: s for s in parse_standards(sample_html)}
    s = by_id[17001]  # Acetylated Vetiver oil, 4 CAS
    assert s.cas_numbers == "84082-84-8 68917-34-0 73246-97-6 62563-80-8"
    assert s.cas_list == ["84082-84-8", "68917-34-0", "73246-97-6", "62563-80-8"]


def test_blank_type_is_preserved(sample_html):
    by_id = {s.document_id: s for s in parse_standards(sample_html)}
    s = by_id[17003]  # Allyl phenoxyacetate
    assert s.type == ""
    assert s.type_label == "Unspecified"


def test_empty_html_raises():
    with pytest.raises(ValueError):
        parse_standards("<html><body>no table</body></html>")


def test_sorted_by_name(sample_html):
    names = [s.name.lower() for s in parse_standards(sample_html)]
    assert names == sorted(names)
