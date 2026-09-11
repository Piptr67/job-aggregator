from unittest.mock import Mock, patch

import requests

from job import Job
from sources.himalayas.source import HimalayasSource


@patch("sources.himalayas.source.requests.get")
def test_fetch_success(mock_get):
    mock_response = Mock()
    mock_response.content = b"<rss>test</rss>"
    mock_get.return_value = mock_response

    source = HimalayasSource(
        "https://test.example/rss",
        10,
    )

    job = Job(
        title="Backend Engineer",
        description="Python backend role",
        link="https://example.com/job",
        pub_date="Mon, 01 Jan 2026 12:00:00 GMT",
        company="Acme Corp",
    )

    with patch.object(source.parser, "parse", return_value=[job]) as mock_parse:
        jobs = source.fetch()

    mock_get.assert_called_once_with(
        "https://test.example/rss",
        timeout=10,
    )
    mock_parse.assert_called_once_with(b"<rss>test</rss>")
    assert jobs == [job]

import pytest

from exceptions import FetchError, ParserError


@patch("sources.himalayas.source.requests.get")
def test_fetch_http_error(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404")
    mock_get.return_value = mock_response

    source = HimalayasSource(
        "https://test.example/rss",
        10,
    )

    with pytest.raises(FetchError, match="Fetching failed"):
        source.fetch()

@patch("sources.himalayas.source.requests.get")
def test_fetch_timeout(mock_get):
    mock_get.side_effect = requests.Timeout("timed out")

    source = HimalayasSource(
        "https://test.example/rss",
        10,
    )

    with pytest.raises(FetchError, match="Fetching took too long"):
        source.fetch()

@patch("sources.himalayas.source.requests.get")
def test_fetch_connection_error(mock_get):
    mock_get.side_effect = requests.ConnectionError("network unavailable")

    source = HimalayasSource(
        "https://test.example/rss",
        10,
    )

    with pytest.raises(FetchError, match="Could not reach the network"):
        source.fetch()


@patch("sources.himalayas.source.requests.get")
def test_fetch_unexpected_request_error(mock_get):
    mock_get.side_effect = requests.RequestException()

    source = HimalayasSource(
        "https://test.example/rss",
        10,
    )

    with pytest.raises(FetchError, match="Unexpected request error"):
        source.fetch()


@patch("sources.himalayas.source.requests.get")
def test_fetch_parser_error(mock_get):
    mock_response = Mock()
    mock_response.content = b"<rss>test</rss>"
    mock_get.return_value = mock_response

    source = HimalayasSource(
        "https://test.example/rss",
        10,
    )

    with patch.object(
        source.parser,
        "parse",
        side_effect=ParserError("Malformed XML"),
    ), pytest.raises(ParserError, match="Malformed XML"):
        source.fetch()