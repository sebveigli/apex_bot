import logging
import os
import sys

from models.database import Database

PLAYER_DB_PATH = os.path.join(os.getcwd(), 'src', 'data', 'db.json')
CONFIG = os.path.join(os.getcwd(), 'src', 'config.json')


def _start_up():
    logging.info("\n********************\nStarting Apex Stats Bot Services\n********************")
    try:
        db = Database(PLAYER_DB_PATH)
    except Exception as e:
        logging.critical(f"""
            Critical error during start-up procedure
            {str(e)}
        """)
        sys.exit(0)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    _start_up()

