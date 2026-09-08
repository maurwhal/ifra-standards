"""Network-free tests for the client: monkeypatch the HTTP layer."""

import pytest

from ifra_standards import client
from ifra_standards.client import IFRAError, discover_config, fetch_raw_html


@pytest.fixture
def no_network(monkeypatch, library_page_html, sample_html):
    calls = []

    def fake_get(url, **kw):
        calls.append(url)
        if url.endswith("/standards-library"):
            return library_page_html
        if "sprig-core/components/render" in url:
            return f"<html><body>{sample_html}</body></html>"
        raise AssertionError(f"unexpected URL {url}")

    monkeypatch.setattr(client, "_get", fake_get)
    return calls


def test_discover_config_extracts_token(no_network):
    token = discover_config()
    assert token.startswith("d34db33f")
    assert '"template":"_sprig\\/standards-library"' in token


def test_fetch_raw_html_uses_two_requests(no_network):
    html = fetch_raw_html()
    assert "IFRA_STD_001.pdf" in html
    assert len(no_network) == 2  # token page + render
    assert "sprig%3Aconfig=" in no_network[1]
    assert "limit=2000" in no_network[1]


def test_fetch_raw_html_with_supplied_config(no_network):
    fetch_raw_html(config="pretend-token", polite_delay=0)
    assert len(no_network) == 1  # render only


def test_pagination_detected(monkeypatch, library_page_html):
    monkeypatch.setattr(
        client, "_get",
        lambda url, **kw: library_page_html
        if url.endswith("standards-library")
        else '<div class="c-pagination">Page 1 of 11</div>',
    )
    with pytest.raises(IFRAError, match="paginated"):
        fetch_raw_html()
