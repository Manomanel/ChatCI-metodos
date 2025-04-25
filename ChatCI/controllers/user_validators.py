from login_exception import LoginException
import re
from database.dao.user_dao import UserDAO

#Interface que delega as classes que vão validar o login do usuário
class IValidator:
    def validate(self, user):
        pass

class NameValidator(IValidator):
    def validate(self, first_name, last_name):
        if not first_name or len(first_name) < 3 or len(first_name) > 20:
            raise LoginException.invalidFirstName()
        if not last_name or len(last_name) < 5 or len(last_name) > 30:
            raise LoginException.invalidLastName()
        
class UsernameValidator(IValidator):
    def __init__(self, userDAO):
        self.userDAO = userDAO
    
    def validate(self, username):
        if username == None:
            raise LoginException.void()
        
        if any(username.isdigit() for char in username):
            raise LoginException.usernameHasNumbers()
        
        if len (username) < 5:
            raise LoginException.charsbelowMinimum()
        
        if len (username) > 15:
            raise LoginException.exceededCharLimit()
        
        if UserDAO.get_user_by_username(username) != None:
            raise LoginException.usernameAlreadyExists(username)

class EmailValidator(IValidator):
    def __init__(self, userDAO):
        self.userDAO = userDAO

    def validate(self, email):
        regex = r"^[\w\.-]+@(ci|academico|di)\.ufpb\.br$"

        if re.match(regex, email) == None:
            raise LoginException.invalidEmail()
        
        if not (UserDAO.get_user_by_email(email)):
            raise LoginException.invalidEmail()
        
class PasswordValidator(IValidator):
    def __init__(self, userDAO):
        self.userDAO = userDAO
        
    def validate(self, password):
        if password == None:
            raise LoginException.invalidPassword()
        
        if len (password) < 10:
            raise LoginException.invalidPassword()
        
        if len(password) > 64:
            raise LoginException.invalidPassword()
        
        if not any(password.isalpha() for char in password):
            raise LoginException.invalidPassword()
        
        if not any(password.isdigit() for char in password):
            raise LoginException.invalidPassword()
        
        if not any(not password.isalnum() for char in password):
            raise LoginException.invalidPassword()
        
        if not any(password.isupper() for char in password):
            raise LoginException.invalidPassword()
        
        if not any(password.islower() for char in password):
            raise LoginException.invalidPassword()