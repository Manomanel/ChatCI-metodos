import re
from user_exception import UserException

# first_name: 20 caracteres
# last_name: 30 caracteres
# email: @ci.ufpb.br ou @academico.ufpb.br ou @di.ufpb.br
# username: 15 caracteres max, 5 caracteres min; verificar se já existe na database; não pode ter número

class UserValidation:
    def __init__(self, userDAO):
        self.userDAO = userDAO

    def validate(user):

        return
    
    def validateEmail(email):
        regex = r"^[\w\.-]+@(ci|academico|di)\.ufpb\.br$"
        if re.match(regex, email) == None:
            raise UserException.invalidEmail()
    
    def validateUsername(username):
        if len (username) < 5:
            raise UserException.usernameBelowMinimum()
        if len (username) > 15:
            raise UserException.usernameExceedCharLimit()
        if userDAO.get_user_by_username(username) != None:
            raise UserException.usernameAlreadyExists(username)