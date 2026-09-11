from unittest.mock import Mock, patch

import pytest
import requests

from exceptions import FetchError, ParserError
from sources.remotive.source import RemotiveSource


@patch("sources.remotive.source.requests.get")
def test_fetch(mock_get):
    response = Mock()
    response.json.return_value = {
        "jobs": [
            {
                "title": "Backend Engineer",
                "description": "Python backend role",
                "url": "https://example.com/job",
                "publication_date": "2026-01-01T12:00:00",
                "company_name": "Acme Corp",
            }
        ]
    }

    mock_get.return_value = response

    source = RemotiveSource(
        "https://example.com/api",
        timeout=10,
    )

    jobs = source.fetch()

    assert len(jobs) == 1
    assert jobs[0].title == "Backend Engineer"
    assert jobs[0].company == "Acme Corp"
    assert jobs[0].link == "https://example.com/job"

    mock_get.assert_called_once_with(
        "https://example.com/api",
        timeout=10,
    )
    response.raise_for_status.assert_called_once()


@patch("sources.remotive.source.requests.get")
def test_fetch_http_error(mock_get):
    mock_get.side_effect = requests.HTTPError("500 Server Error")

    source = RemotiveSource(
        "https://example.com/api",
        timeout=10,
    )

    with pytest.raises(FetchError, match="Fetching failed for URL"):
        source.fetch()


@patch("sources.remotive.source.requests.get")
def test_fetch_timeout(mock_get):
    mock_get.side_effect = requests.Timeout("Request timed out")

    source = RemotiveSource(
        "https://example.com/api",
        timeout=10,
    )

    with pytest.raises(FetchError, match="Fetching took too long for URL"):
        source.fetch()


@patch("sources.remotive.source.requests.get")
def test_fetch_connection_error(mock_get):
    mock_get.side_effect = requests.ConnectionError("Connection failed")

    source = RemotiveSource(
        "https://example.com/api",
        timeout=10,
    )

    with pytest.raises(FetchError, match="Could not reach the network for URL"):
        source.fetch()



@patch("sources.remotive.source.requests.get")
def test_fetch_invalid_json(mock_get):
    response = Mock()
    response.json.side_effect = requests.exceptions.JSONDecodeError(
        "Invalid JSON",
        "response",
        0,
    )
    mock_get.return_value = response

    source = RemotiveSource(
        "https://example.com/api",
        timeout=10,
    )

    with pytest.raises(FetchError, match="Invalid JSON response from URL"):
        source.fetch()


@patch("sources.remotive.source.requests.get")
def test_fetch_parser_error(mock_get):
    response = Mock()
    response.json.return_value = {"jobs": [{}]}
    mock_get.return_value = response

    source = RemotiveSource(
        "https://example.com/api",
        timeout=10,
    )

    with pytest.raises(ParserError, match="Missing required job field"):
        source.fetch()

