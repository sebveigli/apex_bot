from db.tables.leaderboard import Leaderboard
from db.tables.match import Match
from db.tables.server import Server
from db.tables.squad import Squad
from db.tables.tournament import Tournament
from db.tables.update import Update
from db.tables.user import User


def get_user_db():
    return User()

def get_server_db():
    return Server()

def get_update_db():
    return Update()

def get_match_db():
    return Match()

def get_squad_db():
    return Squad()

def get_tournament_db():
    return Tournament()

def get_leaderboard_db():
    return Leaderboard()
