from controllers.user_management import UserManagement
from controllers.user_validation import UserRegistrationValidator
from controllers.user_validators import IValidator, NameValidator, UsernameRegistrationValidator, EmailRegistrationValidator, PasswordValidator, UsernameDBValidator, EmailDBValidator
from controllers.login_exception import LoginException
from entities.user import User
from database.factory.user_dao_factory import UserDAOFactory
from storage.binary_file_adapter import BinaryFileAdapter, ArquivoBinario

class ChatCIFacade:
    def __init__(self):
        self.user = UserManagement()
        #self.msg  = MessageManagement()
        self.user_persistence = UserDAOFactory.get_instance()
        self.file_adapter = BinaryFileAdapter()
        
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
    def cadastrar_usuario(self, nome: str, first_name: str, last_name: str, email: str, tipo: str, senha: str):
        """
        Registra um novo usuário. 
        Retorna o user_id em caso de sucesso, ou None em caso de erro.
        """
        user = User(None, nome, email, senha, first_name, last_name, tipo, False, False)
        validator = UserRegistrationValidator([
            NameValidator(),
            UsernameRegistrationValidator(),
            EmailRegistrationValidator(),
            PasswordValidator(),
            UsernameDBValidator(self.user_persistence),
            EmailDBValidator(self.user_persistence)
        ])
        try:
            validator.validate (user)
        except LoginException as e:
            return None, e.message
        return self.user.adicionar_usuario(user), None

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
    
    
    def atualiza_perfil(self, user_id: int, bio: str, profile_picture = None):
        """
        Atualiza o perfil associado ao usuário"""
        return self.user.atualizar_perfil(user_id, bio, profile_picture)
    
    def restaura_perfil(self, user_id: int):
        return self.user.desfazer_mudancas_perfil(user_id)
    
    def salva_arquivo(self, file_data: bytes, file_name: str) -> bool:
        """
        Salva um arquivo no sistema utilizando a persistência de arquivos binários.
        """
        arquivo = ArquivoBinario(file_data, file_name)
        return self.file_adapter.salva_arquivo_adaptado(arquivo)

    def busca_arquivo(self, file_id: int) -> ArquivoBinario:
        """
        Recupera um arquivo binário do sistema.
        """
        return self.file_adapter.salva_arquivo_adaptado(file_id)