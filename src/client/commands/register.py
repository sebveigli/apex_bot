import logging

from client.tasks.apex.stats import Stats
from client.utils.discord_embed import error_embed, success_embed
from db import get_user_db, get_update_db, get_match_db

VALID_COMMANDS = ["register", "add"]

class Register():
    @staticmethod
    def match(token):
        return token.lower() in VALID_COMMANDS
    
    @staticmethod
    async def execute(message_dispatcher):
        logger = logging.getLogger(__name__)

        data = Stats.make_request(search_term=message_dispatcher.split_message[1], uid_search=False)

        if data.get('Error'):
            return await message_dispatcher.message.channel.send(
                embed=error_embed(
                    description="There was an error retrieving your data from the Respawn servers <@{}> - are you sure you typed the correct Origin account name?".format(message_dispatcher.author_id)
                )
            )

        data = Stats.standardize_response(data, timestamp=None)

        user_db = get_user_db()
        user = user_db.get_users([message_dispatcher.author_id])

        if user is None:
            update_db = get_update_db()
            match_db = get_match_db()

            user_db.add_user(message_dispatcher.author_id, message_dispatcher.server_id, data['profile']['uid'])
            update_db.add_user(message_dispatcher.author_id)
            match_db.add_user(message_dispatcher.author_id)

            return await message_dispatcher.message.channel.send(
                embed=success_embed(
                    description="You have been registered to the bot <@{0}>.\n\nNow tracking you under {1[name]} (uid: {1[uid]})".format(message_dispatcher.author_id, data['profile'])
                )
            )
        else:
            user_db.set_origin_name(message_dispatcher.author_id, data['profile']['uid'])

            return await message_dispatcher.message.channel.send(
                embed=success_embed(
                    description="Your origin name has been updated in the bot <@{0}>.\n\nNow tracking you under {1[name]} (uid: {1[uid]})".format(message_dispatcher.author_id, data['profile'])
                )
            )
