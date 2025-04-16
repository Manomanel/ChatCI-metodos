import re
from user_exception import UserException

# first_name: 20 caracteres
# last_name: 30 caracteres
# email: @ci.ufpb.br ou @academico.ufpb.br ou @di.ufpb.br
# username: 15 caracteres max, 5 caracteres min; verificar se já existe na database; não pode ter número

class UserValidation:
    def __init__(self, userDAO):
        self.userDAO = userDAO

    def validate(self, user):
        self.validateFirstAndLastName(user.firstName, user.lastName)
        self.validateUsername(user.username)
        self.validateEmail(user.email)

    def validateEmail(email):
        regex = r"^[\w\.-]+@(ci|academico|di)\.ufpb\.br$"
        
        if re.match(regex, email) == None:
            raise UserException.invalidEmail()
    
    def validateUsername(username):
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
        
    def validateFirstAndLastName(firstName, lastName):
        if firstName == None:
            raise UserException.void()
        
        if len(firstName) < 3:
            raise UserException.charsbelowMinimum()
        
        if len(firstName) > 20:
            raise UserException.exceededCharLimit()
        
        if lastName == None:
            raise UserException.void()
        
        if len(lastName) < 15:
            raise UserException.charsbelowMinimum()
        
        if len(lastName) > 30:
            raise UserException.exceededCharLimit()