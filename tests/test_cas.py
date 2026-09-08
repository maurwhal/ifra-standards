from ifra_standards.cas import extract_cas, is_valid_cas, split_cas_field


def test_is_valid_cas_known_good():
    assert is_valid_cas("50-00-0")  # formaldehyde
    assert is_valid_cas("127-91-3")  # beta-pinene
    assert is_valid_cas("144020-22-4")


def test_is_valid_cas_bad_check_digit():
    assert not is_valid_cas("50-00-1")
    assert not is_valid_cas("127-91-9")


def test_is_valid_cas_malformed():
    for bad in ("", "not-a-cas", "1234", "50-0-0", "50-00", "RIFM ID: 690"):
        assert not is_valid_cas(bad)


def test_extract_cas_from_messy_string():
    assert extract_cas("127-91-3 (RIFM ID: 690)") == ["127-91-3"]
    assert extract_cas("survey 40/2023, CAS 106-24-1") == ["106-24-1"]


def test_extract_cas_multiple_and_dedup():
    field = "144020-22-4 28371-99-5 144020-22-4"
    assert extract_cas(field) == ["144020-22-4", "28371-99-5"]


def test_split_cas_field_separators():
    assert split_cas_field("5502-75-0; 13828-37-0, 13674-19-6") == [
        "5502-75-0", "13828-37-0", "13674-19-6",
    ]


def test_extract_cas_validation_toggle():
    # "00-00-9" is CAS-shaped but has a wrong check digit
    assert extract_cas("00-00-9") == []
    assert extract_cas("00-00-9", validate=False) == ["00-00-9"]
