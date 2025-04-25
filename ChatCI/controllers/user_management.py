from database.persistence.user_persistence import UserPersistence
from database.persistence.profile_persistence import ProfilePersistence
import logging
import hashlib

logger = logging.getLogger('gerenciador_usuarios')

class UserManagement:
    """
    Classe responsável pela gestão de usuários.
    """
    def __init__(self):
        self.user_persistence = UserPersistence()
        self.profile_dao = ProfilePersistence()
    
    def validar_login(self, email_ou_username, senha):
        """
        Valida o login do usuário.
        """
        try:
            # Verifica se o input é um email ou username
            # caso tenha @ ira diretamente para email, caso contrario vai para username
            if '@' in email_ou_username:
                usuario = self.user_persistence.get_user_by_email(email_ou_username)
            else:
                usuario = self.user_persistence.get_user_by_username(email_ou_username)
            
            if not usuario:
                logger.info(f"Tentativa de login: usuário {email_ou_username} não encontrado")
                return None

            # verifica se a senha esta correta 
            if self._verificar_senha(usuario['password'], senha):
                logger.info(f"Login bem sucedido para o usuário {email_ou_username}")
                return usuario
            else:
                logger.info(f"Tentativa de login: senha incorreta para {email_ou_username}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao validar login: {e}")
            return None
    
    def _verificar_senha(self, senha_hash, senha_texto):
        """
        Verifica se a senha informada é igual ao hash armazenado.
        """
        try:
            partes = senha_hash.split('$')
            if len(partes) != 4:
                return False
                
            algoritmo, iteracoes, salt, hash_armazenado = partes
            iteracoes = int(iteracoes)
            
            # verifica se a senha armazenada é igual ao hash da senha informada
            # usando o mesmo algoritmo, salt e numero de iterações
            # o hash é gerado com o mesmo algoritmo, salt e numero de iterações
            hash_calculado = hashlib.pbkdf2_hmac(
                'sha256',
                senha_texto.encode('utf-8'),
                salt.encode('utf-8'),
                iteracoes
            ).hex()
            
            return hash_calculado == hash_armazenado
            
        except Exception as e:
            logger.error(f"Erro ao verificar senha: {e}")
            return False
    
    def adicionar_usuario(self, nome, email, tipo, senha):
        """
        Adiciona um novo usuário ao sistema.
        """
        try:
            partes_nome = nome.split()
            first_name = partes_nome[0]
            last_name = ' '.join(partes_nome[1:]) if len(partes_nome) > 1 else ''

            is_student = tipo.lower() == "estudante"
            is_professor = tipo.lower() == "professor"

            username = email.split('@')[0]

            username_base = username
            contador = 1
            while self.user_persistence.get_user_by_username(username):
                username = f"{username_base}{contador}"
                contador += 1

            # criacao do usuario
            user_id = self.user_persistence.create_user(
                username=username,
                email=email,
                password=senha,
                first_name=first_name,
                last_name=last_name,
                student=is_student,
                professor=is_professor
            )

            self.profile_dao.create(
                user_id=user_id,
                bio=f"{'Estudante' if is_student else 'Professor'} - Cadastrado via sistema web"
            )
            
            logger.info(f"Usuário {username} ({email}) criado com sucesso!")
            return user_id
            
        except Exception as e:
            logger.error(f"Erro ao adicionar usuário: {e}")
            return None
        
    def get_user_by_id(self, user_id):
        """
        Busca um usuário pelo ID
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dicionário com dados do usuário ou None caso não encontrado
        """
        try:
            return self.user_persistence.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por ID: {e}")
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
            return self.user_persistence.update_user(user_id, **dados)
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {e}")
            return False