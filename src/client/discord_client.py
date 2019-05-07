import asyncio
import discord
import logging
import os

from client.utils.message_dispatcher import MessageDispatcher
from tasks.scheduled_tasks import ScheduledTasks

logger = logging.getLogger(__name__)


class DiscordClient(discord.Client):
    def __init__(self, loop=None, **options):
        super().__init__(loop=loop, **options)


    async def on_ready(self):
        logger.info("Connected to Discord successfully.")
        logger.info("Logged in as @{0.name}#{0.discriminator} [UID: {0.id}] in environment {1}".format(self.user, os.environ["env"]))
        logger.info("Starting background tasks")
        
        asyncio.ensure_future(ScheduledTasks.update_apex(self))


    async def on_message(self, message):
        if message.author.id == self.user.id or message.author.bot:
            return

        await MessageDispatcher(message).dispatch()


    async def on_guild_join(self, guild):
        logger.info("Joined new server {0} ({0.id})".format(guild))
        self.server_db.add_server(guild.id, guild.owner.id, guild.text_channels[0].id)

        await self.get_channel(guild.text_channels[0].id).send("Thanks for inviting <@{0.id}> to your channel.".format(self.user))


    async def on_guild_remove(self, guild):
        logger.info("Removed from server {}.. either the client was kicked/banned, or the server was deleted by the owner :(".format(guild.id))
        self.server_db.delete_server(guild.id)
