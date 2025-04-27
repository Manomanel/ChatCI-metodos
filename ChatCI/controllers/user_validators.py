from controllers.login_exception import LoginException
from database.dao.user_dao import UserDAO
import re
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger('gerenciador_usuarios')

#Interface que delega as classes que vão validar o login do usuário
class IValidator(ABC):
   @abstractmethod
   def validate(self, user):
      pass

class LoginValidator:
    def __init__(self, userDAO):
        self.userDAO = userDAO
        self.user = None

    def validate (self, usernameOrEmail, password):
        #Verifica se o input é um e-mail ou username
        if '@' in usernameOrEmail:
            user = self.userDAO.get_user_by_email(usernameOrEmail)
        else:
            user = self.userDAO.get_user_by_username(usernameOrEmail)

        #Retorna erro se não é um usuário
        if not user:
            logger.info(f'Tentativa de login: {usernameOrEmail} não encontrado')
            raise LoginException.emailorUsernameDoesnotExist()
        
        if not self.passwordValidator(password, user['password']):
            raise LoginException.wrongPassword()
        
        return user

class NameValidator(IValidator):
    def validate(self, user):
        first_name = user.first_name
        last_name = user.last_name
        
        if not first_name or len(first_name) < 3 or len(first_name) > 20:
            raise LoginException.invalidFirstName()
        if not last_name or len(last_name) < 3 or len(last_name) > 30:
            raise LoginException.invalidLastName()
        
class UsernameRegistrationValidator(IValidator):
    def __init__(self):
        return
    
    def validate(self, user):
        username = user.username
        
        if username == None:
            raise LoginException.void()
        
        if any(char.isdigit() for char in username):
            raise LoginException.usernameHasNumbers()
        
        if len (username) < 5:
            raise LoginException.charsBelowMinimum()
        
        if len (username) > 15:
            raise LoginException.exceededCharLimit()
        
class UsernameDBValidator(IValidator):
    def __init__(self, userDAO):
        self.userDAO = userDAO

    def validate(self, user):
        username = user.username

        if self.userDAO.get_user_by_username(username) != None:
            raise LoginException.usernameAlreadyExists(username)

class EmailRegistrationValidator(IValidator):
    def __init__(self):
        return

    def validate(self, user):
        email = user.email
        
        regex = r"^[\w\.-]+@(ci|academico|di)\.ufpb\.br$"

        if re.match(regex, email) == None:
            raise LoginException.invalidEmail()
        
class EmailDBValidator(IValidator):
    def __init__(self, userDAO):
        self.userDAO = userDAO

    def validate (self, user):
        email = user.email
        if not (self.userDAO.get_user_by_email(email)):
            raise LoginException.emailAlreadyExists()

class PasswordValidator(IValidator):
    def __init__(self):
        return 
    
    def validate(self, user):
        password = user.password
        
        if password == None:
            raise LoginException.invalidPasswordRegistration()
        
        if len(password) < 10 or len(password) > 64:
         raise LoginException.invalidPasswordRegistration()
        
        if not any(char.isalpha() for char in password):
            raise LoginException.invalidPasswordRegistration()
        
        if not any(char.isdigit() for char in password):
            raise LoginException.invalidPasswordRegistration()
        
        if not any(not char.isalnum() for char in password):
            raise LoginException.invalidPasswordRegistration()
        
        if not any(char.isupper() for char in password):
            raise LoginException.invalidPasswordRegistration()
        
        if not any(char.islower() for char in password):
            raise LoginException.invalidPasswordRegistration()