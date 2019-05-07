import db
import logging

from client.commands import COMMANDS

logger = logging.getLogger(__name__)

class MessageDispatcher():
    def __init__(self, message):
        self.message = message
        self.server_id = message.guild.id
        self.split_message = message.content.split(' ')

        self.server_db = db.get_server_db()
        self.server_config = self.server_db.get_server(self.server_id)

    async def dispatch(self):
        if not self._is_valid_command():
            return

        for c in COMMANDS:
            if c.match(self.split_message[0][1:]):
                logger.debug("Matched with command class {}".format(c))
                return await c.execute(self.message)

    def _is_valid_command(self):
        return self.split_message[0][0] == self.server_config['prefix']
