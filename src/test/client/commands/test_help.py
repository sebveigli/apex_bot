import pytest

from client.commands.help import Help

def test_match():
    assert Help.match("help") is True

def test_match_case_insensitive():
    assert Help.match("hElP") is True

def test_invalid_match():
    assert Help.match("foo") is False
