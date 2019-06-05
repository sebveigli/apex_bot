import pytest

from client.commands.help import Help

@pytest.fixture(scope='module')
def help():
    return Help()

def test_match(help):
    assert help.match("help") is True

def test_match_case_insensitive(help):
    assert help.match("helP") is True

def test_invalid_match(help):
    assert help.match("foo") is False
