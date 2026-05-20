"""Tests for browser cookie parsing utilities."""

import pytest

from notebooklm_tools.utils.browser import (
    extract_build_label_from_curl,
    extract_csrf_from_curl,
    extract_session_id_from_curl,
    parse_cookies_from_curl,
)
from notebooklm_tools.core.exceptions import AuthenticationError


SAMPLE_CURL = (
    "curl 'https://content-pa.googleapis.com/google.internal.apps.notebooklm.v1alpha1.NotebookLmService/"
    "GetNotebook?alt=json&f.sid=1234567890&bl=20260519.00_p0' \\\n"
    "  -H 'Cookie: SID=abc123; HSID=def456; SSID=ghi789; APISID=jkl012; SAPISID=mno345' \\\n"
    "  -H 'Content-Type: application/json' \\\n"
    "  --data-raw '[[\"FdrFJe\",{\"at\":\"csrf_token_value_abc\",\"params\":{}}]]'"
)


class TestParseCookiesFromCurl:
    def test_parses_cookie_header(self):
        cookies = parse_cookies_from_curl(SAMPLE_CURL)
        assert cookies["SID"] == "abc123"
        assert cookies["HSID"] == "def456"
        assert cookies["SSID"] == "ghi789"
        assert cookies["APISID"] == "jkl012"
        assert cookies["SAPISID"] == "mno345"

    def test_parses_double_quoted_cookie_header(self):
        curl = "curl 'http://example.com' -H \"Cookie: SID=val1; HSID=val2\""
        cookies = parse_cookies_from_curl(curl)
        assert cookies == {"SID": "val1", "HSID": "val2"}

    def test_raises_when_no_cookie_header(self):
        with pytest.raises(AuthenticationError, match="No Cookie header found"):
            parse_cookies_from_curl("curl 'http://example.com'")

    def test_raises_when_empty_cookies(self):
        curl = "curl 'http://example.com' -H 'Cookie: '"
        with pytest.raises(AuthenticationError, match="Could not parse cookies"):
            parse_cookies_from_curl(curl)


class TestExtractCsrfFromCurl:
    def test_extracts_from_data_raw(self):
        csrf = extract_csrf_from_curl(SAMPLE_CURL)
        assert csrf == "csrf_token_value_abc"

    def test_extracts_from_data(self):
        curl = "curl 'http://example.com' --data '[[\"x\",{\"at\":\"my_token\"}]]'"
        assert extract_csrf_from_curl(curl) == "my_token"

    def test_returns_empty_when_no_token(self):
        curl = "curl 'http://example.com' --data-raw '[[\"x\",{}]]'"
        assert extract_csrf_from_curl(curl) == ""


class TestExtractSessionIdFromCurl:
    def test_extracts_f_sid(self):
        sid = extract_session_id_from_curl(SAMPLE_CURL)
        assert sid == "1234567890"

    def test_returns_empty_when_no_sid(self):
        curl = "curl 'http://example.com'"
        assert extract_session_id_from_curl(curl) == ""


class TestExtractBuildLabelFromCurl:
    def test_extracts_bl(self):
        bl = extract_build_label_from_curl(SAMPLE_CURL)
        assert bl == "20260519.00_p0"

    def test_returns_empty_when_no_bl(self):
        curl = "curl 'http://example.com'"
        assert extract_build_label_from_curl(curl) == ""
