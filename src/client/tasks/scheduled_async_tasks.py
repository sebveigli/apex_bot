import asyncio
import logging
import threading
import time

logger = logging.getLogger(__name__)

class ScheduledAsyncTasks():
    @staticmethod
    async def update_client_presence(client):
        from discord import Status, Activity, ActivityType
        from db import get_server_db

        server_count = 0
        
        while True:
            logger.debug("Updating presence on Discord")

            server_db = get_server_db()
            count = server_db.count()

            if count != server_count:
                logger.debug("Server count changed, updating presence")
                
                server_count = count
                message = "{} server{}".format(count, "" if count == 1 else "s")

                activity = Activity(name=message, type=ActivityType.listening)
                await client.change_presence(status=Status.dnd, activity=activity)

            await asyncio.sleep(60)

    @staticmethod
    async def update_tournaments(apex_updater):
        pass

