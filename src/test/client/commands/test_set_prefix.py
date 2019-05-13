import pytest

from unittest.mock import Mock

from client.commands.set_prefix import SetPrefix

class MockMessageDispatcher(Mock):
    server_id = 123456789
    split_message = ["^setprefix", "!"]
    server_db = Mock()

    async def return_async_val(self, val):
        return val

def test_valid_match():
    assert SetPrefix.match("setprefix") is True

def test_valid_match_case_insensitive():
    assert SetPrefix.match("sEtPReFix") is True

def test_invalid_match():
    assert SetPrefix.match("setprefox") is False

@pytest.mark.asyncio
async def test_execute_not_admin():
    mmd = MockMessageDispatcher()

    mmd._is_admin_user.return_value = False
    
    res = await SetPrefix.execute(mmd)

    assert res is None

@pytest.mark.asyncio
async def test_change_prefix_as_admin():
    mmd = MockMessageDispatcher()

    mmd._is_admin_user.return_value = True
    mmd.server_db.set_prefix.return_value = None
    mmd.message.channel.send.return_value = mmd.return_async_val('foo')

    res = await SetPrefix.execute(mmd)

    mmd.server_db.set_prefix.assert_called_with(123456789, "!")
    
