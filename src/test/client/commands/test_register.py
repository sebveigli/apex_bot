import pytest

from unittest.mock import Mock, patch

from client.commands.register import Register

@pytest.fixture(scope='module')
def register():
    return Register()

def test_valid_match(register):
    assert register.match("register") is True

def test_valid_match_case_insensitive(register):
    assert register.match("aDd") is True

def test_invalid_match(register):
    assert register.match("foo") is False

@pytest.mark.asyncio
async def test_invalid_origin_name(mock_message_dispatcher, register):
    mock_message_dispatcher.message.channel.send.return_value = mock_message_dispatcher.return_async_val('foo')
    mock_message_dispatcher.split_message = ['register', 'randomnamethatdoesntexist']

    await register.execute(mock_message_dispatcher)

    mock_message_dispatcher.user_db.get_users.assert_not_called()
    mock_message_dispatcher.user_db.add_user.assert_not_called()
    mock_message_dispatcher.update_db.add_user.assert_not_called()
    mock_message_dispatcher.match_db.add_user.assert_not_called()

@pytest.mark.asyncio
async def test_valid_origin_name_existing_user_update(mock_message_dispatcher, register):
    mock_message_dispatcher.split_message = ['register', 'protent1al']
    mock_message_dispatcher.message.channel.send.return_value = mock_message_dispatcher.return_async_val('foo')

    mock_user_db = Mock()
    mock_user_db.get_users.return_value = [{'user': 123456789, 'origin': 0}]

    protential_uid = 1000141524238

    with patch.object(register, 'get_user_db', return_value=mock_user_db):
        await register.execute(mock_message_dispatcher)

    mock_user_db.get_users.assert_called_with([123456789])
    mock_user_db.add_user.assert_not_called()
    mock_user_db.set_origin_name.assert_called_with(123456789, protential_uid)


@pytest.mark.asyncio
async def test_valid_origin_name_new_user(mock_message_dispatcher, register):
    mock_message_dispatcher.split_message = ['register', 'protent1al']
    mock_message_dispatcher.message.channel.send.return_value = mock_message_dispatcher.return_async_val('foo')

    mock_user_db = Mock()
    mock_update_db = Mock()
    mock_match_db = Mock()

    mock_user_db.get_users.return_value = None

    with patch.object(register, 'get_user_db', return_value=mock_user_db):
        with patch.object(register, 'get_update_db', return_value=mock_update_db):
            with patch.object(register, 'get_match_db', return_value=mock_match_db):
                await register.execute(mock_message_dispatcher)

    protential_uid = 1000141524238

    mock_user_db.get_users.assert_called_with([123456789])
    mock_user_db.add_user.assert_called_with(123456789, 1337, protential_uid)
    mock_update_db.add_user.assert_called_with(123456789)
    mock_match_db.add_user.assert_called_with(123456789)

    mock_message_dispatcher.user_db.set_origin_name.assert_not_called()
