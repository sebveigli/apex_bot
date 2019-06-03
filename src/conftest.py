import pytest

from unittest.mock import Mock

@pytest.fixture(scope='session')
def mock_message_dispatcher():
    class MockMessageDispatcher(Mock):
        author_id = 123456789
        server_id = 1337

        async def return_async_val(self, val):
            return val

    return MockMessageDispatcher()
