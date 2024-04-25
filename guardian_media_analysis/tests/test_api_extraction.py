import pytest
from src.api_extarction import GuardianAPI
import json
import requests
import requests_mock
from datetime import datetime


# Mock data for testing
MOCK_ARTICLES = {
    "response": {
        "status": "ok",
        "total": 1,
        "results": [
            {
                "webTitle": "Justin Trudeau wins second term",
                "webPublicationDate": "2019-10-22",
                "webUrl": "http://example.com/trudeau_wins",
                "apiUrl": "http://example.com/trudeau_wins_api"
            }
        ]
    }
}

@pytest.fixture
def guardian_api():
    """Fixture to instantiate the GuardianAPI class."""
    return GuardianAPI()

def test_successful_data_fetch(guardian_api):
    """Test that the API fetches data successfully and returns correct data."""
    with requests_mock.Mocker() as m:
        m.get("http://content.guardianapis.com/search", json=MOCK_ARTICLES)
        search_query = "Justin Trudeau"
        from_date = "2018-01-01"
        to_date = datetime.now().strftime("%Y-%m-%d")
        articles = guardian_api.guardian_search(search_query, from_date, to_date)
        assert articles == MOCK_ARTICLES['response']['results'], "The fetched articles do not match expected mock data."

def test_api_response_error_handling(guardian_api):
    """Test the API's ability to handle non-200 responses gracefully."""
    with requests_mock.Mocker() as m:
        m.get("http://content.guardianapis.com/search", status_code=500)
        with pytest.raises(Exception):
            search_query = "Justin Trudeau"
            from_date = "2018-01-01"
            to_date = datetime.now().strftime("%Y-%m-%d")
            guardian_api.guardian_search(search_query, from_date, to_date)

def test_data_validation(guardian_api):
    """Test validation of data to ensure all articles are within the requested date range."""
    with requests_mock.Mocker() as m:
        m.get("http://content.guardianapis.com/search", json=MOCK_ARTICLES)
        search_query = "Justin Trudeau"
        from_date = "2018-01-01"
        to_date = "2019-12-31"
        articles = guardian_api.guardian_search(search_query, from_date, to_date)
        for article in articles:
            assert from_date <= article['webPublicationDate'] <= to_date, "Article date out of the requested range."

def test_rate_limit_handling(guardian_api):
    """Test handling of API rate limiting scenario."""
    with requests_mock.Mocker() as m:
        m.get("http://content.guardianapis.com/search", status_code=429, json={"error": "Rate limit exceeded"})
        with pytest.raises(Exception):
            search_query = "Justin Trudeau"
            from_date = "2018-01-01"
            to_date = datetime.now().strftime("%Y-%m-%d")
            guardian_api.guardian_search(search_query, from_date, to_date)