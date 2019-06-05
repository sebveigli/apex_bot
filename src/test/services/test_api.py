from unittest.mock import patch

import pandas as pd
import pytest
import requests

from services.api import API, APIResponseFailure, APITimeoutException


class StubRequest():
    def __init__(self, response, status_code):
        self.text = response
        self.status_code = status_code

@pytest.fixture(scope='function')
def api():
    return API()

def test_uid_search(api):
    users_list = pd.DataFrame.from_records(
        [
            {
                "user": 123,
                "origin": 456
            },
            {
                "user": 987,
                "origin": 654
            }
        ]
    )

    with patch.object(API, '_run', return_value=None):
        api.uid_search(users_list)
        api._run.assert_called_once_with([123, 987])

    assert "uid=456,654" in api.url

def test_player_search(api):
    player = 'protent1al'

    with patch.object(API, '_run', return_value=None):
        api.player_search(player)
        api._run.assert_called_once_with(['protent1al'])

    assert "player=protent1al" in api.url

@patch('requests.get', return_value=StubRequest("{}", 200))
def test_run_valid_response(request, api):
    users = ['protent1al']

    with patch.object(API, '_standardize_response', return_value=[['protent1al', {}]]):
        response = api._run(users)
        assert response == [['protent1al', {}]]

    request.assert_called_once_with("", timeout=10)

@patch('requests.get', return_value=StubRequest("{}", 404))
def test_run_404_response_no_standardize(request, api):
    users = ['protent1al']

    with pytest.raises(APIResponseFailure) as e:
        response = api._run(users)
        api._standardize_response.assert_not_called()

    request.assert_called_once_with("", timeout=10)
    assert "Received failed response from Mozambiquehe.re API with status code 404" in e.exconly()

@patch('requests.get', side_effect=requests.Timeout)
def test_run_timeout_no_standardize(request, api):
    users = ['protent1al']

    with pytest.raises(APITimeoutException) as e:
        response = api._run(users)
        api._standardize_response.assert_not_called()
    
    request.assert_called_once_with("", timeout=10)
    assert "Timeout reached whilst querying Mozambiquehe.re API" in e.exconly()

def test_standardize_response_keep_all_extras(api, example_api_response):
    response_tuple = [['protent1al', example_api_response.get_response()]]
    timestamp = 123

    expected = [
        [
            'protent1al',
            {
                "timestamp": 123,
                "legends": {
                    "Pathfinder": {
                        "data": {"damage": 1000},
                        "ImgAssets": {"icon": "http://foobar.com"},
                    },
                    "Bangalore": {
                        "data": {},
                        "ImgAssets": {"icon": "http://foobar.com"},
                    }
                },
                "realtime": {},
                "total": {"kd": 2},
                "profile": {},
                "selected": {"legend": "Pathfinder", "data": {"damage": 1000, "ImgAssets": {"icon": "http://foobar.com"}}}
            }
        ]
    ]

    result = api._standardize_response(response_tuple, timestamp, remove_img_assets=False, remove_kd=False)

    assert result == expected

def test_standardize_response_remove_img_assets(api, example_api_response):
    response_tuple = [['protent1al', example_api_response.get_response()]]
    timestamp = 123

    expected = [
        [
            'protent1al',
            {
                "timestamp": 123,
                "legends": {
                    "Pathfinder": {
                        "data": {"damage": 1000},
                    },
                    "Bangalore": {
                        "data": {},
                    }
                },
                "realtime": {},
                "total": {"kd": 2},
                "profile": {},
                "selected": {"legend": "Pathfinder", "data": {"damage": 1000}}
             }
        ]
    ]

    result = api._standardize_response(response_tuple, timestamp, remove_img_assets=True, remove_kd=False)

    assert result == expected

def test_standardize_response_remove_kd(api, example_api_response):
    response_tuple = [['protent1al', example_api_response.get_response()]]
    timestamp = 123

    expected = [
        [
            'protent1al',
            {
                "timestamp": 123,
                "legends": {
                    "Pathfinder": {
                        "data": {"damage": 1000},
                        "ImgAssets": {"icon": "http://foobar.com"},
                    },
                    "Bangalore": {
                        "data": {},
                        "ImgAssets": {"icon": "http://foobar.com"},
                    }
                },
                "realtime": {},
                "total": {},
                "profile": {},
                "selected": {"legend": "Pathfinder", "data": {"damage": 1000, "ImgAssets": {"icon": "http://foobar.com"}}}
            }
        ]
    ]

    result = api._standardize_response(response_tuple, timestamp, remove_img_assets=False, remove_kd=True)

    assert result == expected

def test_standardize_discard_error_responses(api, example_api_response):
    response_tuple = [
        ['protent1al', example_api_response.get_response()],
        ['nonexistantuser', {"Error": "Player not found!"}]
    ]
    timestamp = 123

    expected = [
        [
            'protent1al',
            {
                "timestamp": 123,
                "legends": {
                    "Pathfinder": {
                        "data": {"damage": 1000},
                    },
                    "Bangalore": {
                        "data": {},
                    }
                },
                "realtime": {},
                "total": {},
                "profile": {},
                "selected": {"legend": "Pathfinder", "data": {"damage": 1000}}
            }
        ]
    ]

    result = api._standardize_response(response_tuple, timestamp, remove_img_assets=True, remove_kd=True)

    assert result == expected
