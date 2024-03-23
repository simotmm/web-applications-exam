from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, codU, username, password, nickname, propic, creatore, privato):
        self.codU=codU
        self.username=username
        self.password=password
        self.nickname=nickname
        self.propic=propic
        self.creatore=creatore
        self.privato=privato

    def get_id(self):
        return (self.codU)
