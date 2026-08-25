from unittest.mock import Mock
import requests
from scraper.utils import fetch_with_retry, dedupe_rows


def test_fetch_with_retry_returns_text_on_success():
    session = Mock()
    session.get.return_value = Mock(status_code=200, text="<html>ok</html>")
    result = fetch_with_retry(session, "https://example.com", retries=2, timeout=5, backoff_seconds=0)
    assert result == "<html>ok</html>"
    assert session.get.call_count == 1


def test_fetch_with_retry_retries_then_succeeds():
    session = Mock()
    fail_response = Mock(status_code=500, text="")
    ok_response = Mock(status_code=200, text="<html>ok</html>")
    session.get.side_effect = [fail_response, ok_response]
    result = fetch_with_retry(session, "https://example.com", retries=2, timeout=5, backoff_seconds=0)
    assert result == "<html>ok</html>"
    assert session.get.call_count == 2


def test_fetch_with_retry_returns_none_after_exhausting_retries():
    session = Mock()
    session.get.side_effect = requests.exceptions.Timeout()
    result = fetch_with_retry(session, "https://example.com", retries=2, timeout=5, backoff_seconds=0)
    assert result is None
    assert session.get.call_count == 3


def test_dedupe_rows_removes_duplicate_urls_keeping_first():
    rows = [
        {"url": "https://a.com/1", "headline_text": "First"},
        {"url": "https://a.com/2", "headline_text": "Second"},
        {"url": "https://a.com/1", "headline_text": "First duplicate"},
    ]
    result = dedupe_rows(rows)
    assert len(result) == 2
    assert result[0]["headline_text"] == "First"
    assert result[1]["headline_text"] == "Second"
