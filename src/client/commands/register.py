import logging

from client.tasks.apex.stats import Stats
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
        data = Stats.make_request(search_term=origin_name, uid_search=False)

        if not data:
            return error_embed(
                description="There was an error retrieving your data from the Respawn servers <@{}> - are you sure you typed the correct Origin account name?".format(user_id)
            )
        
        data = Stats.standardize_response(data, timestamp=None)

        user_db = self.get_user_db()
        user = user_db.get_users([user_id])

        print(user)

        if user is None:
            update_db = self.get_update_db()
            match_db = self.get_match_db()

            user_db.add_user(user_id, server_id, data['profile']['uid'])
            update_db.add_user(user_id)
            match_db.add_user(user_id)

            return success_embed(
                description="You have been registered to the bot <@{0}>.\n\nNow tracking you under {1[name]} (uid: {1[uid]})".format(user_id, data['profile'])
            )
        else:
            user_db.set_origin_name(user_id, data['profile']['uid'])

            return success_embed(
                description="Your origin name has been updated in the bot <@{0}>.\n\nNow tracking you under {1[name]} (uid: {1[uid]})".format(user_id, data['profile'])
            )
