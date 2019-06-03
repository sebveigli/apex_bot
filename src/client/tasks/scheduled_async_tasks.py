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
    async def update_server_prefix_cache(prefix_cache):
        from db import get_server_db

        while True:
            logger.debug("Updating prefix cache")

            server_db = get_server_db()
            servers = server_db.get_servers()

            for _, server in servers.iterrows():
                server_id = server['server']
                server_prefix = server['prefix']

                if server_id not in prefix_cache or prefix_cache.get(server_id) != server_prefix:
                    logger.debug("Updating prefix cache for server {} with new prefix {}".format(server_id, server_prefix))
                    prefix_cache[server_id] = server_prefix

            await asyncio.sleep(300)
    
    @staticmethod
    async def clear_update_history(apex_player_updater):
        """
        To prevent the update table getting too big from all the updates, the bot should periodically
        clear the updates for all users (who are not actively playing).

        This should run once every hour
        """

        from db import get_user_db, get_update_db

        while True:
            while apex_player_updater.running:
                await asyncio.sleep(1)

            logger.info("Doing cleanup of update table...")

            user_db = get_user_db()
            update_db = get_update_db()

            users = user_db.get_users()
            
            for _, user in users.iterrows():
                if user.get('apex'):
                    if user['apex'].get('state') == 'offline':
                        logger.debug("Cleaning up user {}".format(user['user']))

                        update_db.clear_updates(user['user'])
            await asyncio.sleep(3600)

    @staticmethod
    async def update_tournaments(apex_updater):
        pass

