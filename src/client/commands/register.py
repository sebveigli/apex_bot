import logging

from services.api import API, APIResponseFailure, APITimeoutException
from client.commands.command import Command
from client.utils.discord_embed import error_embed, success_embed

VALID_COMMANDS = ["register", "add"]

class Register(Command):
    def __init__(self):
        super().__init__(VALID_COMMANDS)

    async def execute(self, message_dispatcher):
        logger = logging.getLogger(__name__)

        full_command = message_dispatcher.split_message[1:]

        if len(full_command) == 1:
            return await message_dispatcher.message.channel.send(embed=self.register_user(message_dispatcher.author_id, full_command[0], message_dispatcher.server_id))
        elif len(full_command) == 2:
            if len(message_dispatcher.message.mentions) > 0:
                mentioned = message_dispatcher.message.mentions[0].id

                for subcommand in full_command:
                    if str(mentioned) not in subcommand:
                        return await message_dispatcher.message.channel.send(embed=self.register_user(mentioned, subcommand, message_dispatcher.server_id))
        else:
            return await message_dispatcher.message.channel.send(
                embed=error_embed(
                    description="Invalid usage of command."
                )
            )

    def register_user(self, user_id, origin_name, server_id):
        api = API()
        
        try:
            data = api.player_search(player_name=origin_name)

        except APIResponseFailure:
            return error_embed(
                description="Couldn't find this user on Origin, are you sure you typed the right name?"
            )

        except APITimeoutException:
            return error_embed(
                description="Connection to the Origin servers timed-out. Please try again shortly."
            )

        origin_uid = data[0][1]['profile']['uid']

        user_db = self.get_user_db()
        user = user_db.get_users([user_id])

        if user is None:
            update_db = self.get_update_db()
            match_db = self.get_match_db()

            user_db.add_user(user_id, server_id, origin_uid)
            update_db.add_user(user_id)
            match_db.add_user(user_id)

            return success_embed(
                description="You have been registered to the bot <@{0}>.\n\nNow tracking you under {1[name]} (uid: {1[uid]})".format(user_id, data[0][1]['profile'])
            )
        else:
            user_db.set_origin_name(user_id, origin_uid)

            return success_embed(
                description="Your origin name has been updated in the bot <@{0}>.\n\nNow tracking you under {1[name]} (uid: {1[uid]})".format(user_id, data[0][1]['profile'])
            )
