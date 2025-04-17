class LoginException (Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    @staticmethod
    def void() -> 'LoginException':
        return LoginException('Campo obrigatório não pode ser passado em branco')
    
    @staticmethod
    def exceededCharLimit() -> 'LoginException':
        return LoginException('Excedeu o limite de caracteres!')
    
    @staticmethod
    def charsBelowMinimum() -> 'LoginException':
        return LoginException('Abaixo da menor quantidade de caracteres!')
    
    @staticmethod
    def invalidEmail() -> 'LoginException':
        return LoginException('E-mail inválido!')
    
    @staticmethod
    def usernameAlreadyExists(username) -> 'LoginException':
        return LoginException(f'username {username} já existe!')
    
    @staticmethod
    def usernameHasNumbers(username) -> 'LoginException':
        return LoginException('Não pode ter números!')
    
    @staticmethod
    def invalidFirstName() -> 'LoginException':
        return LoginException('Nome inválido!')
    
    @staticmethod
    def invalidLastName() -> 'LoginException':
        return LoginException('Sobrenome inválido!')
    
    @staticmethod
    def invalidPassword(password) -> 'LoginException':
        return LoginException('Senha inválida!')