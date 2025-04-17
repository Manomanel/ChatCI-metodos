class UserException (Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    @staticmethod
    def void() -> 'UserException':
        return UserException('Campo obrigatório não pode ser passado em branco')
    
    @staticmethod
    def exceededCharLimit() -> 'UserException':
        return UserException('Excedeu o limite de caracteres!')
    
    @staticmethod
    def charsbelowMinimum() -> 'UserException':
        return UserException('Abaixo da menor quantidade de caracteres!')
    
    @staticmethod
    def invalidEmail() -> 'UserException':
        return UserException('E-mail inválido!')
    
    @staticmethod
    def usernameAlreadyExists(username) -> 'UserException':
        return UserException(f'username {username} já existe!')
    
    @staticmethod
    def usernameHasNumbers(username) -> 'UserException':
        return UserException('Não pode ter números!')
    
    @staticmethod
    def invalidFirstName() -> 'UserException':
        return UserException('Nome inválido!')
    
    @staticmethod
    def invalidLastName() -> 'UserException':
        return UserException('Sobrenome inválido!')
    
    @staticmethod
    def invalidPassword(password) -> 'UserException':
        return UserException('Senha inválida!')