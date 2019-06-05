from unittest.mock import Mock, patch, call

import pandas as pd
import pytest

import db

@pytest.fixture(scope='module')
def stat_updater():
    with patch.object(db, 'get_user_db', return_value=Mock()), \
        patch.object(db, 'get_update_db', return_value=Mock()), \
        patch.object(db, 'get_match_db', return_value=Mock()):

        from services.stat_updater import StatUpdater

        return StatUpdater(discord_client=None)

@pytest.fixture(scope='function', autouse=True)
def reset_mocks(stat_updater):
    stat_updater.user_db.reset_mock()
    stat_updater.update_db.reset_mock()
    stat_updater.match_db.reset_mock()


def test_state_from_offline_to_online(stat_updater):
    stat_updater.user_db.get_users.return_value = pd.DataFrame.from_records([{"apex": {"state": "offline"}}])

    user = 123456789
    states = dict(online=True, start_game=False, finish_game=False, changed_legend=False)
    timestamp = 123

    expected = dict(
        user_id=123456789,
        state='online',
        last_session_started=123,
        timestamp=123
    )

    stat_updater._update_player_state(user, states, timestamp=timestamp)

    stat_updater.user_db.set_state.assert_called_once_with(**expected)

def test_state_from_offline_to_in_game(stat_updater):
    stat_updater.user_db.get_users.return_value = pd.DataFrame.from_records([{"apex": {"state": "offline", "last_session_started": None}}])

    user = 123456789
    states = dict(online=True, start_game=True, finish_game=False, changed_legend=False)
    timestamp = 123

    online_change_expected = dict(
        user_id=123456789,
        state='online',
        last_session_started=123,
        timestamp=123
    )

    in_game_change_expected = dict(
        user_id=123456789,
        state='in_game',
        last_session_started=123,
        timestamp=123
    )

    stat_updater._update_player_state(user, states, timestamp=timestamp)

    calls = [call(**online_change_expected), call(**in_game_change_expected)]

    stat_updater.user_db.set_state.assert_has_calls(calls)

def test_state_from_online_to_in_game(stat_updater):
    stat_updater.user_db.get_users.return_value = pd.DataFrame.from_records([{"apex": {"state": "online", "last_session_started": 100}}])

    user = 123456789
    states = dict(online=True, start_game=True, finish_game=False, changed_legend=False)
    timestamp = 123

    state_change_expected = dict(
        user_id=123456789,
        state='in_game',
        last_session_started=100,
        timestamp=123
    )

    stat_updater._update_player_state(user, states, timestamp=timestamp)

    stat_updater.user_db.set_state.assert_called_once_with(**state_change_expected)

def test_state_from_online_to_offline(stat_updater):
    stat_updater.user_db.get_users.return_value = pd.DataFrame.from_records([{"apex": {"state": "online", "last_session_started": 100}}])

    user = 123456789
    states = dict(online=False, start_game=False, finish_game=False, changed_legend=False)
    timestamp = 123

    state_change_expected = dict(
        user_id=123456789,
        state='offline',
        last_session_started=100,
        timestamp=123
    )

    stat_updater._update_player_state(user, states, timestamp=timestamp)

    stat_updater.user_db.set_state.assert_called_once_with(**state_change_expected)

def test_state_from_in_game_to_online(stat_updater):
    stat_updater.user_db.get_users.return_value = pd.DataFrame.from_records([{"apex": {"state": "in_game", "last_session_started": 100}}])

    user = 123456789
    states = dict(online=True, start_game=False, finish_game=True, changed_legend=False)
    timestamp = 123

    state_change_expected = dict(
        user_id=123456789,
        state='online',
        last_session_started=100,
        timestamp=123
    )

    stat_updater._update_player_state(user, states, timestamp=timestamp)

    stat_updater.user_db.set_state.assert_called_once_with(**state_change_expected)

def test_state_from_in_game_to_offline(stat_updater):
    stat_updater.user_db.get_users.return_value = pd.DataFrame.from_records([{"apex": {"state": "in_game", "last_session_started": 100}}])

    user = 123456789
    states = dict(online=False, start_game=False, finish_game=True, changed_legend=False)
    timestamp = 123

    state_change_online_expected = dict(
        user_id=123456789,
        state='online',
        last_session_started=100,
        timestamp=123
    )
    
    state_change_offline_expected = dict(
        user_id=123456789,
        state='offline',
        last_session_started=100,
        timestamp=123
    )

    stat_updater._update_player_state(user, states, timestamp=timestamp)

    calls = [call(**state_change_online_expected), call(**state_change_offline_expected)]

    stat_updater.user_db.set_state.assert_has_calls(calls)

def test_get_match_data_invalid_legend_change(stat_updater):
    """
    In this test the user manages to change their character going between in-game -> online state changes

    We cannot do anything with this data, because the API will only pick up updates on the active banner on
    the account, and if the user changed, it means the match data will not be reflected
    """

    user = 123

    old_data = {
        "selected": {
            "legend": "Pathfinder",
            "data": {
                "damage": 100,
                "kills": 0,
                "headshots": 15
            }
        }
    }

    new_data = {
        "selected": {
            "legend": "Banglore",
            "data": {
                "damage": 50,
                "kills": 3,
                "headshots": 9
            }
        }
    }

    match_data = stat_updater._save_match_data(user, old_data, new_data)

    assert match_data is None
    stat_updater.match_db.add_match.assert_not_called()

def test_get_match_data_valid_match(stat_updater):
    user = 123

    old_data = {
        "selected": {
            "legend": "Pathfinder",
            "data": {
                "damage": 100,
                "kills": 0,
                "headshots": 15
            }
        },
        "timestamp": 123
    }

    new_data = {
        "selected": {
            "legend": "Pathfinder",
            "data": {
                "damage": 150,
                "kills": 3,
                "headshots": 15
            }
        },
        "timestamp": 124
    }

    expected_match_data = {
        "started": 123,
        "ended": 124,
        "legend": "Pathfinder",
        "stats": {
            "damage": 50,
            "kills": 3,
            "headshots": 0
        }
    }

    match_data = stat_updater._save_match_data(user, old_data, new_data)

    assert match_data == expected_match_data
    stat_updater.match_db.add_match.assert_called_once_with(user, expected_match_data)
