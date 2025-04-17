from user_exception import UserException
import re

#Interface que delega as classes que vão validar o login do usuário
class IValidator:
    def validate(self, user):
        pass

class NameValidator(IValidator):
    def validate(self, first_name, last_name):
        if not first_name or len(first_name) < 3 or len(first_name) > 20:
            raise UserException.invalidFirstName()
        if not last_name or len(last_name) < 5 or len(last_name) > 30:
            raise UserException.invalidLastName()
        
class UsernameValidator(IValidator):
    def __init__(self, userDAO):
        self.userDAO = userDAO
    
    def validate(self, username):
        if username == None:
            raise UserException.void()
        
        if any(username.isdigit() for char in username):
            raise UserException.usernameHasNumbers()
        
        if len (username) < 5:
            raise UserException.charsbelowMinimum()
        
        if len (username) > 15:
            raise UserException.exceededCharLimit()
        
        if userDAO.get_user_by_username(username) != None:
            raise UserException.usernameAlreadyExists(username)

class EmailValidator(IValidator):
    def __init__(self, userDAO):
        self.userDAO = userDAO

    def validate(self, email):
        regex = r"^[\w\.-]+@(ci|academico|di)\.ufpb\.br$"

        if re.match(regex, email) == None:
            raise UserException.invalidEmail()
        
        if not (userDAO.get_user_by_email(email)):
            raise UserException.invalidEmail()
        
class PasswordValidator(IValidator):
    def __init__(self, userDAO):
        self.userDAO = userDAO
        
    def validate(self, password):
        if password == None:
            raise UserException.invalidPassword()
        
        if len (password) < 10:
            raise UserException.invalidPassword()
        
        if len(password) > 64:
            raise UserException.invalidPassword()
        
        if not any(password.isalpha() for char in password):
            raise UserException.invalidPassword()
        
        if not any(password.isdigit() for char in password):
            raise UserException.invalidPassword()
        
        if not any(not password.isalnum() for char in password):
            raise UserException.invalidPassword()
        
        if not any(password.isupper() for char in password):
            raise UserException.invalidPassword()
        
        if not any(password.islower() for char in password):
            raise UserException.invalidPassword()