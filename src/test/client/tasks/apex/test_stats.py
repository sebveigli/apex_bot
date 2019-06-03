import pytest

from unittest.mock import Mock, patch

from client.tasks.apex.stats import Stats

import requests
import pandas as pd


class StubRequest():
    def __init__(self, response, status_code):
        self.text = response
        self.status_code = status_code

@pytest.fixture(scope='module')
def stats():
    return Stats()

@pytest.fixture(scope='module')
def example_api_response():
    class Make:
        def get_response(self):
            return {
                "legends": {
                    "selected": {
                        "Pathfinder": {
                            "damage": 1000,
                            "ImgAssets": {"icon": "http://foobar.com"},
                        }
                    },
                    "all": {
                        "Pathfinder": {
                            "data": {"damage": 1000},
                            "ImgAssets": {"icon": "http://foobar.com"},
                        },
                        "Bangalore": {
                            "ImgAssets": {"icon": "http://foobar.com"},
                        }
                    }
                },
                "realtime": {},
                "total": {"kd": 2},
                "global": {},
                "mozambiquehere_internal": {},
            }

    return Make()

def test_get_stats_for_single_valid_user(stats):
    users = pd.DataFrame.from_dict({"origin": [123],"user": [111]})

    with patch.object(Stats, 'make_request', return_value={"selected": "Pathfinder"}) as mocked_make_request:
        valid, invalid = stats.get_update(users)

        mocked_make_request.assert_called_once_with(search_term="123", uid_search=True)
        assert len(valid) == 1
        assert len(invalid) == 0

        assert valid == [[111, {"selected": "Pathfinder"}]]

def test_get_stats_for_multiple_valid_users(stats):
    users = pd.DataFrame.from_dict({"origin": [123, 456],"user": [111, 222]})

    with patch.object(Stats, 'make_request', return_value=[{"selected": "Pathfinder"}, {"selected": "Bangalore"}]) as mocked_make_request:
        valid, invalid = stats.get_update(users)

        mocked_make_request.assert_called_once_with(search_term="123,456", uid_search=True)
        assert len(valid) == 2
        assert len(invalid) == 0

        assert valid == [[111, {"selected": "Pathfinder"}],[222, {"selected": "Bangalore"}]]

def test_get_stats_single_valid_single_invalid(stats):
    users = pd.DataFrame.from_dict({"origin": [123, 456],"user": [111, 222]})

    with patch.object(Stats, 'make_request', return_value=[{"selected": "Pathfinder"}, {"Error": "User does not exist"}]) as mocked_make_request:
        valid, invalid = stats.get_update(users)

        mocked_make_request.assert_called_once_with(search_term="123,456", uid_search=True)
        assert len(valid) == 1
        assert len(invalid) == 1

        assert valid == [[111, {"selected": "Pathfinder"}]]
        assert invalid == [222]

def test_get_stats_multiple_invalid(stats):
    users = pd.DataFrame.from_dict({"origin": [123, 456],"user": [111, 222]})

    with patch.object(Stats, 'make_request', return_value=[{"Error": "User does not exist"}, {"Error": "User does not exist"}]) as mocked_make_request:
        valid, invalid = stats.get_update(users)

        mocked_make_request.assert_called_once_with(search_term="123,456", uid_search=True)
        assert len(valid) == 0
        assert len(invalid) == 2

        assert invalid == [111, 222]

@patch('requests.get', return_value=StubRequest("{}", 200))
def test_make_uid_search(request, stats):
    result = stats.make_request("123,456", uid_search=True)

    args, kwargs = request.call_args

    assert "uid=123,456" in args[0]
    assert 10 == kwargs.get('timeout')
    assert result == {}

@patch('requests.get', return_value=StubRequest("{}", 200))
def test_make_player_name_search(request, stats):
    result = stats.make_request("protent1al,mercyatmyhand", uid_search=False)

    args, kwargs = request.call_args

    assert "player=protent1al,mercyatmyhand" in args[0]
    assert 10 == kwargs.get('timeout')
    assert result == {}

@patch('requests.get', return_value=StubRequest("{}", 404))
def test_non_200_status_code(request, stats):
    result = stats.make_request("protent1al", uid_search=False)

    args, kwargs = request.call_args

    assert "player=protent1al" in args[0]
    assert 10 == kwargs.get('timeout')
    assert result == None

@patch('requests.get', side_effect=requests.Timeout)
def test_timeout(request, stats):
    result = stats.make_request("protent1al", uid_search=False)

    args, kwargs = request.call_args

    assert "player=protent1al" in args[0]
    assert 10 == kwargs.get('timeout')
    assert result == None

def test_standardize_response_keep_all_extras(stats, example_api_response):
    timestamp = 123

    expected = {
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

    result = stats.standardize_response(example_api_response.get_response(), timestamp, no_img_assets=False, ignore_kd=False)

    assert result == expected

def test_standardize_response_remove_img_assets(stats, example_api_response):
    timestamp = 123

    expected = {
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

    result = stats.standardize_response(example_api_response.get_response(), timestamp, no_img_assets=True, ignore_kd=False)

    assert result == expected

def test_standardize_response_remove_kd(stats, example_api_response):
    timestamp = 123

    expected = {
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

    result = stats.standardize_response(example_api_response.get_response(), timestamp, no_img_assets=False, ignore_kd=True)

    assert result == expected

def test_should_update_db_start_game(stats, example_api_response):
    old_response = example_api_response.get_response()
    new_response = example_api_response.get_response()

    old_response['realtime']['isOnline'] = 1
    new_response['realtime']['isOnline'] = 1

    old_response['realtime']['isInGame'] = 0
    new_response['realtime']['isInGame'] = 1
    
    old_response['realtime']['selectedLegend'] = "Pathfinder"
    new_response['realtime']['selectedLegend'] = "Pathfinder"

    should_update, states = stats.should_update_db(old_response, new_response)

    assert should_update is True
    assert states == dict(online=True, start_game=True, finish_game=False, changed_legend=False)

def test_should_update_db_end_game(stats, example_api_response):
    old_response = example_api_response.get_response()
    new_response = example_api_response.get_response()

    old_response['realtime']['isOnline'] = 1
    new_response['realtime']['isOnline'] = 1

    old_response['realtime']['isInGame'] = 1
    new_response['realtime']['isInGame'] = 0
    
    old_response['realtime']['selectedLegend'] = "Pathfinder"
    new_response['realtime']['selectedLegend'] = "Pathfinder"

    should_update, states = stats.should_update_db(old_response, new_response)

    assert should_update is True
    assert states == dict(online=True, start_game=False, finish_game=True, changed_legend=False)

def test_should_update_db_changed_legend(stats, example_api_response):
    old_response = example_api_response.get_response()
    new_response = example_api_response.get_response()

    old_response['realtime']['isOnline'] = 1
    new_response['realtime']['isOnline'] = 1

    old_response['realtime']['isInGame'] = 0
    new_response['realtime']['isInGame'] = 0
    
    old_response['realtime']['selectedLegend'] = "Pathfinder"
    new_response['realtime']['selectedLegend'] = "Bangalore"

    should_update, states = stats.should_update_db(old_response, new_response)

    assert should_update is True
    assert states == dict(online=True, start_game=False, finish_game=False, changed_legend=True)

def test_should_update_db_no_data_history(stats, example_api_response):
    old_response = None
    new_response = example_api_response.get_response()

    new_response['realtime']['isOnline'] = 1
    new_response['realtime']['isInGame'] = 0
    new_response['realtime']['selectedLegend'] = "Bangalore"

    should_update, states = stats.should_update_db(old_response, new_response)

    assert should_update is True
    assert states == None

def test_shouldnt_update_db_went_online(stats, example_api_response):
    old_response = example_api_response.get_response()
    new_response = example_api_response.get_response()

    old_response['realtime']['isOnline'] = 0
    new_response['realtime']['isOnline'] = 1

    old_response['realtime']['isInGame'] = 0
    new_response['realtime']['isInGame'] = 0
    
    old_response['realtime']['selectedLegend'] = "Pathfinder"
    new_response['realtime']['selectedLegend'] = "Pathfinder"

    should_update, states = stats.should_update_db(old_response, new_response)

    assert should_update is False
    assert states == dict(online=True, start_game=False, finish_game=False, changed_legend=False)

