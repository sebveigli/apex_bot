import logging

from client.commands import commands
from db import get_server_db

logger = logging.getLogger(__name__)

class MessageDispatcher():
    def __init__(self, message):
        self.message = message
        self.author_id = message.author.id
        self.server_id = message.guild.id
        self.split_message = message.content.split(' ')

        self.server_db = get_server_db()
        self.server_config = self.server_db.get_servers([self.server_id]).iloc[0]

    async def dispatch(self):
        if not self._is_valid_command():
            return

        for c in commands:
            if c.match(self.split_message[0][1:]):
                logger.debug("Matched with command class {}".format(c))
                try:
                    return await c.execute(self)
                except Exception as e:
                    logger.critical(str(e))

    def _is_valid_command(self):
        return self.split_message[0][0] == self.server_config['prefix']

    def _is_admin_user(self):
        print(self.server_config['owner'])
        return self.author_id in self.server_config['admins'] or self.author_id == self.server_config['owner']