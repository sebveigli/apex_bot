import asyncio
import logging
import os
import traceback

import discord

logger = logging.getLogger(__name__)


class DiscordClient(discord.Client):
    def __init__(self, loop=None, **options):
        super().__init__(loop=loop, **options)

        self.scheduled_tasks = self.loop.create_task(
            self._dump_message_queue()
        )

    async def on_ready(self):
        logger.info("Connected to Discord successfully.")
        logger.info("Logged in as @{0.name}#{0.discriminator} [UID: {0.id}] in environment {1}".format(self.user, os.environ["env"]))
    
    async def on_message(self, message):
        logger.info("Saw message!")
    
    async def _dump_message_queue(self):
        await self.wait_until_ready()

        while not self.is_closed():
            try:
                logger.info("Fetching & Sending Messages")
                # wait for something
            except Exception as e:
                logger.critical(traceback.print_tb(e.__traceback__))
            finally:
                await asyncio.sleep(60)
