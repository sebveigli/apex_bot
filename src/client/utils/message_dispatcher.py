import logging

from client.commands import commands
from db import get_server_db

logger = logging.getLogger(__name__)

class MessageDispatcher():
    def __init__(self, message):
        self.server_db = get_server_db()

        self.message = message
        self.author_id = message.author.id
        self.split_message = message.content.split(' ')

        if message.guild:
            self.server_id = message.guild.id
            self.server_config = self.server_db.get_servers([self.server_id]).iloc[0]
        else:
            self.server_id = None
            self.server_config = None

    async def dispatch(self):
        if not self._is_valid_command():
            return
        
        if not self.server_id:
            return await self.no_pms_message()

        for c in commands:
            if c.match(self.split_message[0][1:]):
                logger.debug("Matched with command class {}".format(c))
                try:
                    return await c.execute(self)
                except Exception as e:
                    logger.critical(str(e))

    def _is_valid_command(self):
        if not self.server_id:
            return True
        return self.split_message[0][0] == self.server_config['prefix']

    def _is_admin_user(self):
        import config

        if not self.server_id:
            return self.author_id == config.OWNER_ID

        return self.author_id in self.server_config['admins'] or self.author_id == self.server_config['owner']

    async def no_pms_message(self):
        from client.utils.discord_embed import error_embed

        await self.message.channel.send(
            embed=error_embed(
                description="Sorry, I don't currently support commands via private messages.. however this will be added eventually, stay tuned :)"
            )
        )
