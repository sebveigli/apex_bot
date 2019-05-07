import asyncio
import logging
import time
import threading

import db

from tasks.apex.stats import Stats

logger = logging.getLogger(__name__)

class ScheduledTasks():
    @staticmethod
    async def update_apex(client):
        while True:
            logger.debug("Running background tasks")
            message_queue = []

            # Update Stats
            updated_users = Stats.scheduled_update()

            check_squads = []
            check_leaderboards = []
            

            for user in updated_users:
                (user_id, state_changes) = user[0], user[1]

                # if 'offline' in 
                print("Updated {} - {}".format(user_id, ",".join(state_changes)))
            # Notify Users

            # Update Squads

            # Notify Users

            # Update Tournaments

            # Notify Users


            logger.debug("Background tasks complete - sleeping")
            await asyncio.sleep(10)

    @staticmethod
    async def update_tournaments(client):
        pass


