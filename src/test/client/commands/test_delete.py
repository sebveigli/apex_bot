import pytest

from unittest.mock import Mock, patch

from client.commands.delete import Delete

@pytest.fixture(scope='module')
def delete():
    return Delete()

def test_valid_match(delete):
    assert delete.match("delete") is True

def test_valid_match_case_insensitive(delete):
    assert delete.match("reMOVE") is True

def test_invalid_match(delete):
    assert delete.match("foo") is False

@pytest.mark.asyncio
async def test_delete_on_non_registered_user(mock_message_dispatcher, delete):
    mock_message_dispatcher.message.channel.send.return_value = mock_message_dispatcher.return_async_val('foo')

    mock_user_db = Mock()
    mock_user_db.get_users.return_value = None

    with patch.object(delete, 'get_user_db', return_value=mock_user_db):
        await delete.execute(mock_message_dispatcher)

    mock_user_db.delete_user.assert_not_called()

@pytest.mark.asyncio
async def test_delete_on_registered_user(mock_message_dispatcher, delete):
    mock_message_dispatcher.message.channel.send.return_value = mock_message_dispatcher.return_async_val('foo')

    mock_user_db = Mock()
    mock_user_db.get_users.return_value = [{'user': 123456789}]

    with patch.object(delete, 'get_user_db', return_value=mock_user_db):
        await delete.execute(mock_message_dispatcher)

    mock_user_db.delete_user.assert_called_once_with(123456789)
