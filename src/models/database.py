import logging
import os
import time

from tinydb import TinyDB, Query

class Database():
    def __init__(self, path):
        self.path = path
        self.db = None
        self.tables = {
            "registered_players": None,
            "stats_cache": None
        }

        self.setup()

    def setup(self):
        logging.info("Loading database...")

        if not os.path.isfile(self.path):
            logging.info("No database found, creating at %s" % str(self.path))
            try:
                with open(self.path, 'w+') as f:
                    logging.info("Database created")
                    f.close()
            except:
                logging.critical("Something went wrong whilst creating database")
                raise

        self.db = TinyDB(self.path)

        for table in self.tables:
            logging.info("Initialising table %s" % table)
            self.tables[table] = self.db.table(table)
    
    def register(self, player):
        logging.info("Attempting to register player {} for platform {}".format(player.name, player.platform))
        
        Player = Query()
        
        rp_db = self.tables['registered_players']

        if len(rp_db.search((Player.name == player.name) & (Player.platform == player.platform))) > 0:
            logging.info("Player already exists - skipping")
            return
        
        try:
            data = {
                **player.to_db(),
                "registered_at": int(round(time.time()*1000)),
                "last_updated": 0, 
                "uid": len(rp_db.all())
            }

            rp_db.insert(data)
        except Exception as e:
            logging.error("Error adding player {} into DB [{}]".format(player.name, e.args))
            raise
        
        logging.info("Player %s registered" % player.name)

