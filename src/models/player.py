import logging

from errors.errors import InvalidConsoleException

VALID_CONSOLES = ["PC", "ORIGIN", "PS4", "PSN", "XBOX"]

class Player():
    def __init__(self, name, platform):
        if platform.upper() not in VALID_CONSOLES:
            raise InvalidConsoleException("{} is not a valid platform (valid: {})".format(platform, VALID_CONSOLES))

        self.name = name
        self.platform = platform.upper()

    def apex_tracker_parser(self):
        pass
    
    def to_db(self):
        return dict(name=self.name, platform=self.platform)
