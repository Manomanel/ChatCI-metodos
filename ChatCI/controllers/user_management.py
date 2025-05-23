from database.factory.user_dao_factory import UserDAOFactory
from database.persistence.profile_persistence import ProfilePersistence
from controllers.user_validation import UserValidation
from controllers.user_validators import IValidator, NameValidator, UsernameRegistrationValidator, LoginValidator
from controllers.login_exception import  LoginException
import logging
import hashlib
from business.login_txt_report_generator import LoginTxtReportGenerator
from business.login_html_report_generator import LoginHtmlReportGenerator
from business.login_pdf_report_generator import LoginPdfReportGenerator


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
            txt_gen = LoginTxtReportGenerator()
            txt_gen.generateReport(usuario)

            html_gen = LoginHtmlReportGenerator()
            html_gen.generateReport(usuario)

            pdf_gen = LoginPdfReportGenerator()
            pdf_gen.generateReport(usuario)
            return usuario
        except LoginException as e:
            logger.error(f'Erro de login ou senha: {e}')
            return None
    
    def adicionar_usuario(self, user):
        try:
            # Gera username único se necessário
            username_base = user.username
            contador = 1
            while self.userDAO.get_user_by_username(user.username):
                user.username = f"{username_base}{contador}"  # Corrigido para modificar user.username
                contador += 1

            is_student = user.tipo.lower() == "estudante"
            is_professor = user.tipo.lower() == "professor"

            user_id = self.userDAO.create_user(
                username=user.username,
                email=user.email,
                password=user.password,
                first_name=user.first_name,
                last_name=user.last_name,
                student=is_student,
                professor=is_professor,
                is_superuser=user.is_superuser  # Adicionado parâmetro
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
        
    #CARETAKER DO MEMENTO
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