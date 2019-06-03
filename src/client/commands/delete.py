import logging

from client.commands.command import Command
from client.utils.discord_embed import error_embed, success_embed

VALID_COMMANDS = ["delete", "remove"]

class Delete(Command):
    def __init__(self):
        super().__init__(VALID_COMMANDS)

    async def execute(self, message_dispatcher):
        logger = logging.getLogger(__name__)

        user_db = self.get_user_db()
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
