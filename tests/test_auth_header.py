"""Authorization header parsing.

`Authorization.split(" ")[1]` raised IndexError on a header without a space,
and the endpoints return str(e) to the caller, so clients saw the raw Python
message "list index out of range" instead of anything actionable.
"""

import pytest
from app_server.main import _bearer_token


def test_extracts_the_token():
    assert _bearer_token("Bearer abc.def.ghi") == "abc.def.ghi"


def test_scheme_is_case_insensitive():
    assert _bearer_token("bearer abc") == "abc"


def test_surrounding_whitespace_is_trimmed():
    assert _bearer_token("Bearer   abc  ") == "abc"


@pytest.mark.parametrize("header", [None, ""])
def test_missing_header_is_reported_as_missing(header):
    with pytest.raises(ValueError, match="missing"):
        _bearer_token(header)


@pytest.mark.parametrize(
    "header",
    [
        "Bearer",  # no space at all -- the IndexError case
        "Bearer ",  # scheme only
        "abc.def.ghi",  # bare token, no scheme
        "Basic dXNlcjpwYXNz",  # wrong scheme
    ],
)
def test_malformed_header_is_rejected_clearly(header):
    with pytest.raises(ValueError) as excinfo:
        _bearer_token(header)

    assert "list index out of range" not in str(excinfo.value)
