import pytest

from unittest.mock import Mock

from client.commands.delete import Delete

class MockMessageDispatcher(Mock):
    author_id = 123456789

    async def return_async_val(self, val):
        return val

def test_valid_match():
    assert Delete.match("delete") is True

def test_valid_match_case_insensitive():
    assert Delete.match("reMOVE") is True

def test_invalid_match():
    assert Delete.match("foo") is False

@pytest.mark.asyncio
async def test_execute_not_user():
    mmd = MockMessageDispatcher()
    
    mmd.user_db.get_users.return_value = None
    mmd.user_db.delete_user.return_value = None
    mmd.message.channel.send.return_value = mmd.return_async_val('foo')

    res = await Delete.execute(mmd)

    assert mmd.message.channel.send.called
    assert not mmd.user_db.delete_user.called

@pytest.mark.asyncio
async def test_delete_user():
    mmd = MockMessageDispatcher()
    
    mmd.user_db.get_users.return_value = [{'user': 123456789}]
    mmd.user_db.delete_user.return_value = None
    mmd.message.channel.send.return_value = mmd.return_async_val('foo')

    res = await Delete.execute(mmd)

    mmd.user_db.delete_user.assert_called_with(mmd.author_id)
    assert mmd.message.channel.send.called
