from db.tables.user import User
from db.tables.server import Server
from db.tables.update import Update
from db.tables.match import Match

def get_user_db():
    return User()

def get_server_db():
    return Server()

def get_update_db():
    return Update()

def get_match_db():
    return Match()
