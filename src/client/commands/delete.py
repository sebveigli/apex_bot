import logging

from client.utils.discord_embed import error_embed, success_embed
from db import get_user_db

VALID_COMMANDS = ["delete", "remove"]

class Delete():
    @staticmethod
    def match(token):
        return token.lower() in VALID_COMMANDS
    
    @staticmethod
    async def execute(message_dispatcher):
        logger = logging.getLogger(__name__)

        user_db = get_user_db()
        user = user_db.get_users([message_dispatcher.author_id])

        if user is None:
            return await message_dispatcher.message.channel.send(
               embed=error_embed(
                   description="Couldn't find you in the users database - are you sure you're registered?"
               )
            )
        else:
            logger.debug("Removing user {} from the database.".format(message_dispatcher.author_id))
            user_db.delete_user(message_dispatcher.author_id)
            return await message_dispatcher.message.channel.send(
                embed=success_embed(
                    description="Successfully removed you from the database. Hope to see you back soon!"
                )
            )
