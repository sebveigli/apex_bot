"""
Don't forget to rename from config.example.py to config.py
"""

"""
OWNER_ID is the user ID of 'super admin' of this bot.

To find your user ID, right click yourself in Discord and hit 'Copy ID'
"""
OWNER_ID = 12345678901234567

"""
DISCORD_BOT_TOKEN is the token that you get from the Discord dashboard to associate a bot account.

Get your token from https://discordapp.com/developers/applications
"""
DISCORD_BOT_TOKEN = "ThiSisJusTaRaNdOmFaKETok3N.InS3Rt uRs h3R3!" # Token for BOT client

"""
LOG_NAME is the name of the log file you want for this particular environment.

Logs will be stored in the root directory of the bot in the folder /logs/
"""
LOG_NAME = "apexbot_dev.log"

"""
MOZAMBIQUE_HERE_API_KEY is your API key for http://mozambiquehe.re.

You will need to request a key for yourself there in order to track Apex stats.
"""
MOZAMBIQUE_HERE_API_KEY = "yourapikeygoeshere"

"""
Mongo DB is the database used for this bot.

Please setup Mongo on your machine, and then configure it correctly in the dictionary below.
"""
MONGO = {
    "host": "localhost",
    "port": 27017,
    "name": "apexbot_dev",
    "username": "",
    "password": "",
    "authSource": ""
}
