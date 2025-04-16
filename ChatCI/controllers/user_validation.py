from user_validators import IValidator

# first_name: 20 caracteres
# last_name: 30 caracteres
# email: @ci.ufpb.br ou @academico.ufpb.br ou @di.ufpb.br
# username: 15 caracteres max, 5 caracteres min; verificar se já existe na database; não pode ter número

class UserValidation:
    def __init__(self, validators: list[IValidator], userDAO):
        self.validators = validators #Criar os validadores em User Control
        self.userDAO = userDAO

    def validate(self, user):
        for validator in self.validators:
            validator.validate(user)