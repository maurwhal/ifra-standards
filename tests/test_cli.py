import csv
import json

from ifra_standards.cli import main


def test_fetch_from_raw_writes_csv(tmp_path, sample_html):
    raw = tmp_path / "raw.html"
    raw.write_text(sample_html, encoding="utf-8")
    out = tmp_path / "out.csv"
    rc = main(["fetch", "--from-raw", str(raw), "-o", str(out)])
    assert rc == 0
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert len(rows) == 4


def test_fetch_stable_drops_timestamp(tmp_path, sample_html):
    raw = tmp_path / "raw.html"
    raw.write_text(sample_html, encoding="utf-8")
    out = tmp_path / "out.json"
    main(["fetch", "--from-raw", str(raw), "--stable", "-o", str(out)])
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "retrieved_at" not in data[0]


def test_diff_command(tmp_path, sample_html):
    raw = tmp_path / "raw.html"
    raw.write_text(sample_html, encoding="utf-8")
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    main(["fetch", "--from-raw", str(raw), "-o", str(a)])
    main(["fetch", "--from-raw", str(raw), "-o", str(b)])
    changes = tmp_path / "changes.md"
    rc = main(["diff", str(a), str(b), "-o", str(changes)])
    assert rc == 0
    assert "No changes" in changes.read_text(encoding="utf-8")


def test_bad_format_returns_1(tmp_path, sample_html):
    raw = tmp_path / "raw.html"
    raw.write_text(sample_html, encoding="utf-8")
    rc = main(["fetch", "--from-raw", str(raw), "-o", str(tmp_path / "x.txt")])
    assert rc == 1
