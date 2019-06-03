import db

class Command():
    def __init__(self, valid_tokens):
        self.valid_tokens = valid_tokens

    def match(self, token):
        return token.lower() in self.valid_tokens
    
    def get_user_db(self):
        return db.get_user_db()

    def get_update_db(self):
        return db.get_update_db()
    
    def get_match_db(self):
        return db.get_match_db()

    def get_server_db(self):
        return db.get_server_db()
