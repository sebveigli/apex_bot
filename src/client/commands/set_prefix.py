VALID_COMMANDS = ["setprefix"]

import logging

class SetPrefix():
    @staticmethod
    def match(token):
        return token.lower() in VALID_COMMANDS
    
    @staticmethod
    async def execute(message_dispatcher):
        logger = logging.getLogger(__name__)
        
        if not message_dispatcher._is_admin_user():
            logger.info("User {} tried to use command {}, but does not have admin rights.".format(message_dispatcher.message.author_id, message_dispatcher.message.content))
            return

        from client.utils.discord_embed import informational_embed
        
        new_prefix = message_dispatcher.split_message[1][0]

        logger.debug("Setting new prefix {} for server {}".format(new_prefix, message_dispatcher.server_id))

        message_dispatcher.server_db.set_prefix(message_dispatcher.server_id, new_prefix)
        await message_dispatcher.message.channel.send(embed=informational_embed(
            description="New prefix has been set for the server, you can now talk to me using {}".format(new_prefix)
        ))
