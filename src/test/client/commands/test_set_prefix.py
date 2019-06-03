import pytest

from unittest.mock import Mock, patch

from client.commands.set_prefix import SetPrefix

@pytest.fixture(scope='module')
def set_prefix():
    return SetPrefix()

def test_valid_match(set_prefix):
    assert set_prefix.match("setprefix") is True

def test_valid_match_case_insensitive(set_prefix):
    assert set_prefix.match("sEtPReFix") is True

def test_invalid_match(set_prefix):
    assert set_prefix.match("setprefox") is False

@pytest.mark.asyncio
async def test_execute_not_admin(mock_message_dispatcher, set_prefix):
    mock_message_dispatcher._is_admin_user.return_value = False
    
    mock_server_db = Mock()
    
    with patch.object(set_prefix, 'get_server_db', return_value=mock_server_db):
        await set_prefix.execute(mock_message_dispatcher)

    mock_server_db.assert_not_called()

@pytest.mark.asyncio
async def test_change_prefix_as_admin(mock_message_dispatcher, set_prefix):
    mock_message_dispatcher.message.channel.send.return_value = mock_message_dispatcher.return_async_val('foo')

    mock_message_dispatcher._is_admin_user.return_value = True
    mock_message_dispatcher.split_message = ["setprefix", "!"]
    
    mock_server_db = Mock()
    
    with patch.object(set_prefix, 'get_server_db', return_value=mock_server_db):
        await set_prefix.execute(mock_message_dispatcher)

    mock_server_db.set_prefix.assert_called_with(1337, "!")
