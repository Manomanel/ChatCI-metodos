from database.factory.user_dao_factory import UserDAOFactory
from database.persistence.profile_persistence import ProfilePersistence
from controllers.user_validation import UserValidation
from controllers.user_validators import IValidator, NameValidator, UsernameRegistrationValidator, LoginValidator
from controllers.login_exception import  LoginException
import logging
import hashlib
from business.login_report_generator import LoginReportGenerator

logger = logging.getLogger('gerenciador_usuarios')

class UserManagement:
    """
    Classe responsável pela gestão de usuários.
    """
    def __init__(self):
        self.userDAO = UserDAOFactory.get_instance()
        self.profile_dao = ProfilePersistence()
        self.validator = None
    
    def validar_login(self, email_ou_username, senha):
        validator = LoginValidator(self.userDAO) 
        try:
            usuario = validator.validate(email_ou_username, senha)
            logger.info(f'Login bem sucedido para o usuário {email_ou_username}')
            # → Gera o relatório de login:
            generator = LoginReportGenerator()
            generator.generateReport(usuario)
            return usuario
            return usuario
        except LoginException as e:
            logger.error(f'Erro de login ou senha: {e}')
            return None
    
    def adicionar_usuario(self, user):
        """
        Adiciona um novo usuário ao sistema.
        """
        try:
            #partes_nome = nome.split()
            #first_name = partes_nome[0]
            #last_name = ' '.join(partes_nome[1:]) if len(partes_nome) > 1 else ''
            #username = email.split('@')[0]

            is_student = user.tipo.lower() == "estudante"
            is_professor = user.tipo.lower() == "professor"

            username_base = user.username
            contador = 1
            while self.userDAO.get_user_by_username(user.username):
                username = f"{username_base}{contador}"
                contador += 1

            # criacao do usuario
            user_id = self.userDAO.create_user(
                username=user.username,
                email=user.email,
                password=user.password,
                first_name=user.first_name,
                last_name=user.last_name,
                student=is_student,
                professor=is_professor
            )

            self.profile_dao.create(
                user_id=user_id,
                bio=f"{'Estudante' if is_student else 'Professor'} - Cadastrado via sistema web"
            )
            
            logger.info(f"Usuário {user.username} ({user.email}) criado com sucesso!")
            return user_id
            
        except Exception as e:
            logger.error(f"Erro ao adicionar usuário: {e}")
            return None

    def atualizar_usuario(self, user_id, **dados):
        """
        Atualiza dados de um usuário
        
        Args:
            user_id: ID do usuário
            **dados: Dados a serem atualizados
            
        Returns:
            True se o usuário foi atualizado, False caso contrário
        """
        try:
            return self.userDAO.update_user(user_id, **dados)
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {e}")
            return False
        
    def atualizar_perfil (self, user_id, bio = None, profile_picture = None):
        try:
            self.profile_dao.save_memento(user_id)

            return self.profile_dao.update(user_id, bio, profile_picture)
        except Exception as e:
            logger.error(f"Erro ao atualizar: {e}")
            return False
        
    def desfazer_mudancas_perfil(self, user_id):
        try:
            return self.profile_dao.restore_last_memento(user_id)
        except Exception as e:
            logger.error(f"Erro ao restaurar o perfil: {e}")
            return False