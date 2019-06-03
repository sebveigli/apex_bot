import logging

from client.commands.command import Command
from client.utils.discord_embed import error_embed, success_embed, informational_embed

VALID_COMMANDS = ["setprefix"]

class SetPrefix(Command):
    def __init__(self):
        super().__init__(VALID_COMMANDS)
    
    async def execute(self, message_dispatcher):
        logger = logging.getLogger(__name__)

        if not message_dispatcher._is_admin_user():
            logger.info("User {} tried to use command {}, but does not have admin rights.".format(message_dispatcher.author_id, message_dispatcher.message.content))
            return
 
        server_db = self.get_server_db()

        new_prefix = message_dispatcher.split_message[1][0]

        logger.debug("Setting new prefix {} for server {}".format(new_prefix, message_dispatcher.server_id))

        server_db.set_prefix(message_dispatcher.server_id, new_prefix)
        await message_dispatcher.message.channel.send(embed=informational_embed(
            description="New prefix has been set for the server, you can now talk to me using {}".format(new_prefix)
        ))
