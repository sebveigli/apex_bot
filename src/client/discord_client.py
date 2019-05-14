import asyncio
import discord
import logging
import os
import threading

from db import get_server_db

from client.utils.message_dispatcher import MessageDispatcher
from client.tasks.scheduled_async_tasks import ScheduledAsyncTasks
from client.tasks.apex_player_updater import ApexPlayerUpdater

logger = logging.getLogger(__name__)


class DiscordClient(discord.Client):
    def __init__(self, loop=None, **options):
        super().__init__(loop=loop, **options)

        """
        Run the ApexPlayerUpdater in a seperate Thread to the Discord Client

        This ensures that the I/O doesn't get blocked during updates and can still respond to command.

        ApexPlayerUpdater overwrites the standard Python threading and implements a variable for whether
        it is running. This can be used to prevent race conditions whilst stats are being updated.
        """
        self.apex_player_updater = ApexPlayerUpdater()

    async def on_ready(self):
        logger.info("Connected to Discord successfully.")
        logger.info("Logged in as @{0.name}#{0.discriminator} [UID: {0.id}]".format(self.user))
        logger.info("Starting background tasks")
        
        asyncio.ensure_future(ScheduledAsyncTasks.update_client_presence(self))
        # asyncio.ensure_future(ScheduledTasks.update_tournaments(self.apex_updater))
        self.apex_player_updater.start()


    async def on_message(self, message):
        if message.author.id == self.user.id or message.author.bot:
            return

        asyncio.ensure_future(MessageDispatcher(message).dispatch())

    async def on_guild_join(self, guild):
        logger.info("Joined new server {0} ({0.id})".format(guild))

        server_db = get_server_db()

        server_db.add_server(guild.id, guild.owner.id, guild.text_channels[0].id)

        await self.get_channel(guild.text_channels[0].id).send("Thanks for inviting <@{0.id}> to your channel.".format(self.user))

    async def on_guild_remove(self, guild):
        logger.info("Removed from server {}.. either the client was kicked/banned, or the server was deleted by the owner :(".format(guild.id))
        
        server_db = get_server_db()

        server_db.delete_server(guild.id)
