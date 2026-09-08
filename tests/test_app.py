"""Network-free tests for the double-click app entry point."""

from datetime import date

import ifra_standards.app as app
from ifra_standards.parse import parse_standards


def test_check_flag_no_network(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["app", "--check"])
    rc = app.main()
    assert rc == 0
    assert "ok" in capsys.readouterr().out.lower()


def test_saves_csv_to_desktop(tmp_path, monkeypatch, capsys, sample_html):
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    monkeypatch.setattr(app, "_desktop", lambda: desktop)
    monkeypatch.setattr("sys.argv", ["app"])
    monkeypatch.setattr("builtins.input", lambda *a: "")
    monkeypatch.setattr(
        "ifra_standards.fetch_standards",
        lambda *a, **k: parse_standards(sample_html),
    )

    rc = app.main()
    assert rc == 0
    out = list(desktop.glob("IFRA Standards *.csv"))
    assert len(out) == 1
    assert date.today().isoformat() in out[0].name
    assert "Done" in capsys.readouterr().out


def test_error_is_shown_and_window_waits(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(app, "_desktop", lambda: tmp_path)
    monkeypatch.setattr("sys.argv", ["app"])
    monkeypatch.setattr("builtins.input", lambda *a: "")
    monkeypatch.setattr(
        "ifra_standards.fetch_standards",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("site changed")),
    )

    rc = app.main()
    assert rc == 1
    text = capsys.readouterr().out
    assert "Something went wrong" in text
    assert "site changed" in text
    assert "issues" in text
