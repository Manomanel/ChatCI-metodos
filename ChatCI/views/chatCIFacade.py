from controllers.user_management import UserManagement

class ChatCIFacade:
    def __init__(self):
        self.user = UserManagement()
        #self.msg  = MessageManagement()
        
    #login
    def login(self, email_ou_username: str, senha: str):
        """
        Tenta autenticar um usuário. 
        Retorna o dict do usuário em caso de sucesso, ou None caso falhe.
        """
        return self.user.validar_login(email_ou_username, senha)

    def logout(self, session: dict):
        """
        Limpa a sessão carregada.
        """
        session.clear()
    
    #cadastro
    def cadastrar_usuario(self, nome: str, email: str, tipo: str, senha: str):
        """
        Registra um novo usuário. 
        Retorna o user_id em caso de sucesso, ou None em caso de erro.
        """
        return self.user.adicionar_usuario(nome, email, tipo, senha)

    def buscar_usuario_por_id(self, user_id: int):
        """
        Retorna o dict de usuário para exibição ou edição.
        """
        return self.user.get_user_by_id(user_id)

    def atualizar_usuario(self, user_id: int, **dados):
        """
        Atualiza campos de um usuário existente.
        Retorna True se OK, False se falhar.
        """
        return self.user.atualizar_usuario(user_id, **dados)
    
    #perfil
    def buscar_perfil(self, user_id: int):
        """
        Retorna o perfil associado (bio, foto, etc.).
        """
        return self.user.profile_dao.get_by_user_id(user_id)