from ifra_standards.diff import diff_standards, format_markdown, load_export
from ifra_standards.export import write
from ifra_standards.models import Standard
from ifra_standards.parse import parse_standards


def _std(doc_id, name, **kw):
    base = {
        "document_id": doc_id, "name": name, "cas_numbers": "1-1-1", "type": "R",
        "amendment": "49", "publication_date": "2020-01", "pdf_url": "x",
        "retrieved_at": "t",
    }
    base.update(kw)
    return Standard(**base)


def test_added_removed_changed():
    old = [_std(1, "Alpha"), _std(2, "Beta"), _std(3, "Gamma", amendment="49")]
    new = [_std(2, "Beta"), _std(3, "Gamma", amendment="52"), _std(4, "Delta")]
    d = diff_standards(old, new)
    assert [s.document_id for s in d["added"]] == [4]
    assert [s.document_id for s in d["removed"]] == [1]
    assert len(d["changed"]) == 1
    std, deltas = d["changed"][0]
    assert std.document_id == 3
    assert deltas["amendment"] == ("49", "52")


def test_no_changes():
    a = [_std(1, "Alpha")]
    assert diff_standards(a, list(a)) == {"added": [], "removed": [], "changed": []}
    assert format_markdown(diff_standards(a, list(a))).strip() == "No changes."


def test_load_export_roundtrip(sample_html, tmp_path):
    standards = parse_standards(sample_html)
    path = write(standards, tmp_path / "s.json")
    loaded = load_export(path)
    assert {s.document_id for s in loaded} == {s.document_id for s in standards}
    assert diff_standards(standards, loaded)["changed"] == []
