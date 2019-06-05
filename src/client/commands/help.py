import logging

from services.api import API, APIResponseFailure, APITimeoutException
from client.commands.command import Command
from client.utils.discord_embed import error_embed, success_embed

VALID_COMMANDS = ["register", "add"]

VALID_COMMANDS = ["help", "h", "?", "halp", "how", "commands"]

class Help(Command):
    def __init__(self):
        super().__init__(VALID_COMMANDS)

    async def execute(self, message_dispatcher):
        from client.utils.discord_embed import informational_embed

        await message_dispatcher.message.channel.send(embed=informational_embed(
            description="Help coming soon!",
            url="http://protenti.al"
        ))
