class User:
    def __init__ (self, userid: int, username: str, email: str, password: str, first_name: str, last_name: str, tipo: str, email_verified: bool, is_superuser: bool):
        self.userid = userid
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.tipo = tipo
        self.email_verified = email_verified
        self.is_superuser = is_superuser