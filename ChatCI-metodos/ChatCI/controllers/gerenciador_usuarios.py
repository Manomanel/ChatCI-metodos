# controllers/gerenciador_usuarios.py
from database.dao.user_dao import UserDAO
from database.dao.profile_dao import ProfileDAO
import logging

logger = logging.getLogger('gerenciador_usuarios')

class GerenciadorUsuarios:
    def __init__(self):
        self.user_dao = UserDAO()
        self.profile_dao = ProfileDAO()
    
    def validar_login(self, email_ou_username, senha):
        """
        Valida o login do usuário
        
        Args:
            email_ou_username: Email ou nome de usuário
            senha: Senha do usuário
            
        Returns:
            Dicionário com dados do usuário se o login for válido, None caso contrário
        """
        try:
            # Verifica se o input é um email ou username
            if '@' in email_ou_username:
                usuario = self.user_dao.get_user_by_email(email_ou_username)
            else:
                usuario = self.user_dao.get_user_by_username(email_ou_username)
            
            if not usuario:
                logger.info(f"Tentativa de login: usuário {email_ou_username} não encontrado")
                return None
                
            # Aqui precisamos verificar a senha
            # Como implementamos uma senha compatível com Django, precisamos de uma função para verificar
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
        Verifica se a senha em texto corresponde ao hash armazenado
        
        Args:
            senha_hash: Hash da senha no formato do Django
            senha_texto: Senha em texto plano
            
        Returns:
            True se a senha estiver correta, False caso contrário
        """
        import hashlib
        
        # Formato do Django: algorithm$iterations$salt$hash
        try:
            partes = senha_hash.split('$')
            if len(partes) != 4:
                return False
                
            algoritmo, iteracoes, salt, hash_armazenado = partes
            iteracoes = int(iteracoes)
            
            # Calcula o hash da senha fornecida
            hash_calculado = hashlib.pbkdf2_hmac(
                'sha256',
                senha_texto.encode('utf-8'),
                salt.encode('utf-8'),
                iteracoes
            ).hex()
            
            # Compara os hashes
            return hash_calculado == hash_armazenado
            
        except Exception as e:
            logger.error(f"Erro ao verificar senha: {e}")
            return False
    
    def adicionar_usuario(self, nome, email, tipo, senha, curso, matricula):
        """
        Adiciona um novo usuário ao sistema
        
        Args:
            nome: Nome completo do usuário
            email: Email do usuário
            tipo: Tipo de usuário ("Estudante" ou "Professor")
            senha: Senha do usuário
            
        Returns:
            ID do usuário criado ou None em caso de erro
        """
        try:
            # Separar o nome em first_name e last_name
            partes_nome = nome.split()
            first_name = partes_nome[0]
            last_name = ' '.join(partes_nome[1:]) if len(partes_nome) > 1 else ''
            
            # Verificar o tipo de usuário
            is_student = tipo.lower() == "estudante"
            is_professor = tipo.lower() == "professor"
            
            # Gerar um username baseado no email
            username = email.split('@')[0]
            
            # Verificar se o username já existe, e adicionar um número se necessário
            username_base = username
            contador = 1
            while self.user_dao.get_user_by_username(username):
                username = f"{username_base}{contador}"
                contador += 1
            
            # Criar o usuário
            user_id = self.user_dao.create_user(
                username=username,
                email=email,
                password=senha,
                first_name=first_name,
                last_name=last_name,
                student=is_student,
                professor=is_professor,
                curso=curso,
                matricula=matricula
                )
            
            # Criar um perfil para o usuário
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
            return self.user_dao.get_user_by_id(user_id)
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
            return self.user_dao.update_user(user_id, **dados)
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {e}")
            return False