from db.services.user_db_service import UserDBService
from db.services.server_db_service import ServerDBService
from db.services.update_db_service import UpdateDBService

def get_user_db():
    return UserDBService()

def get_server_db():
    return ServerDBService()

def get_update_db():
    return UpdateDBService()