import pytest

from unittest.mock import Mock

from client.commands.register import Register

class MockMessageDispatcher(Mock):
    server_id = 1337
    author_id = 123456789

    async def return_async_val(self, val):
        return val

def test_valid_match():
    assert Register.match("register") is True

def test_valid_match_case_insensitive():
    assert Register.match("aDd") is True

def test_invalid_match():
    assert Register.match("foo") is False

@pytest.mark.asyncio
async def test_invalid_origin_name():
    mmd = MockMessageDispatcher()
    
    mmd.split_message = ['foobar', 'foobarbaz123']
    mmd.message.channel.send.return_value = mmd.return_async_val('foo')

    await Register.execute(mmd)

    assert mmd.message.channel.send.called
    assert not mmd.user_db.get_users.called
    assert not mmd.user_db.add_user.called
    assert not mmd.update_db.add_user.called
    assert not mmd.match_db.add_user.called

@pytest.mark.asyncio
async def test_valid_origin_name_existing_user_update():
    mmd = MockMessageDispatcher()

    protential_uid = 1000141524238
    
    mmd.split_message = ['foobar', 'protent1al']
    mmd.user_db.get_users.return_value = [{'user': 123456789, 'origin': 0}]

    mmd.message.channel.send.return_value = mmd.return_async_val('foo')

    await Register.execute(mmd)

    mmd.user_db.get_users.assert_called_with([123456789])
    mmd.user_db.set_origin_name.assert_called_with(123456789, protential_uid)
    
    assert mmd.message.channel.send.called
    assert not mmd.user_db.add_user.called
    assert not mmd.update_db.add_user.called
    assert not mmd.match_db.add_user.called

@pytest.mark.asyncio
async def test_valid_origin_name_new_user():
    mmd = MockMessageDispatcher()

    protential_uid = 1000141524238
    mmd.split_message = ['foobar', 'protent1al']
    mmd.user_db.get_users.return_value = None

    mmd.message.channel.send.return_value = mmd.return_async_val('foo')

    await Register.execute(mmd)

    mmd.user_db.get_users.assert_called_with([123456789])
    mmd.user_db.add_user.assert_called_with(123456789, 1337, protential_uid)
    mmd.update_db.add_user.assert_called_with(123456789)
    mmd.match_db.add_user.assert_called_with(123456789)

    assert mmd.message.channel.send.called
    assert not mmd.user_db.set_origin_name.called
