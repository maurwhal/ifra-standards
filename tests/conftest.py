from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_html() -> str:
    """A saved slice of a rendered Standards Library table (a few rows)."""
    return (FIXTURES / "render_sample.html").read_text(encoding="utf-8")


@pytest.fixture
def library_page_html() -> str:
    """A minimal stand-in for the standards-library page with a config token."""
    return (FIXTURES / "library_page_stub.html").read_text(encoding="utf-8")
