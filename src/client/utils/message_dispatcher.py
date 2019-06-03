import logging

from client.commands import commands
from client.utils.discord_embed import error_embed
from db import get_server_db

logger = logging.getLogger(__name__)

class MessageDispatcher():
    def __init__(self, message):
        self.message = message
        self.author_id = message.author.id
        self.split_message = message.content.split(' ')

        if message.guild:
            self.server_id = message.guild.id
        else:
            self.server_id = None

    async def dispatch(self, prefix_cache):
        if not self.server_id:
            return await self.no_pms_message()
        
        if not self._is_valid_command(prefix_cache):
            return

        for c in commands:
            if c.match(self.split_message[0][1:]):
                return await c.execute(self)

    async def no_pms_message(self):
        await self.message.channel.send(
            embed=error_embed(
                description="Sorry, I don't currently support commands via private messages.. however this will be added eventually, stay tuned :)"
            )
        )

    def _is_valid_command(self, prefix_cache):
        return self.split_message[0][0] == prefix_cache.get(self.server_id)

    def _is_admin_user(self):
        server_config = get_server_db().get_servers([self.server_id]).iloc[0]

        return self.author_id in server_config['admins'] or self.author_id == server_config['owner']
