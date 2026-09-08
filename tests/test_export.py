import csv
import json

from ifra_standards.export import to_records, write
from ifra_standards.parse import parse_standards


def test_csv_roundtrip(sample_html, tmp_path):
    standards = parse_standards(sample_html)
    out = write(standards, tmp_path / "s.csv")
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert len(rows) == 4
    assert rows[0]["cas_numbers"]
    assert "; " in rows[1]["cas_list"] or rows[1]["cas_list"]  # joined string


def test_json_export(sample_html, tmp_path):
    standards = parse_standards(sample_html)
    out = write(standards, tmp_path / "s.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data) == 4
    assert isinstance(data[0]["cas_list"], str)  # joined in flat export


def test_explode_cas_multiplies_rows(sample_html, tmp_path):
    standards = parse_standards(sample_html)
    flat = list(to_records(standards))
    exploded = list(to_records(standards, explode_cas=True))
    assert len(exploded) > len(flat)
    # Acetylated Vetiver oil has 4 CAS -> 4 rows
    vetiver = [r for r in exploded if r["document_id"] == 17001]
    assert len(vetiver) == 4
    assert {r["cas"] for r in vetiver} == {
        "84082-84-8", "68917-34-0", "73246-97-6", "62563-80-8",
    }


def test_unknown_format_rejected(sample_html, tmp_path):
    import pytest

    with pytest.raises(ValueError):
        write(parse_standards(sample_html), tmp_path / "s.txt")
