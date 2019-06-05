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

@pytest.fixture(scope='session')
def example_api_response():
    class GetResponse:
        def get_response(self):
            return {
                "legends": {
                    "selected": {
                        "Pathfinder": {
                            "damage": 1000,
                            "ImgAssets": {"icon": "http://foobar.com"},
                        }
                    },
                    "all": {
                        "Pathfinder": {
                            "data": {"damage": 1000},
                            "ImgAssets": {"icon": "http://foobar.com"},
                        },
                        "Bangalore": {
                            "ImgAssets": {"icon": "http://foobar.com"},
                        }
                    }
                },
                "realtime": {},
                "total": {"kd": 2},
                "global": {},
                "mozambiquehere_internal": {},
                "event": {},
            }

    return GetResponse()