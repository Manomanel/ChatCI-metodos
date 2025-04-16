class UserException (Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
    
    @staticmethod
    def void() -> 'UserException':
        return UserException('Campo obrigatório não pode ser passado em branco')
    
    @staticmethod
    def usernameExceedCharLimit() -> 'UserException':
        return UserException('Excedeu o limite de caracteres!')
    
    @staticmethod
    def usernameBelowMinimum() -> 'UserException':
        return UserException('Abaixo da menor quantidade de caracteres!')
    
    @staticmethod
    def invalidEmail() -> 'UserException':
        return UserException('E-mail inválido!')
    
    