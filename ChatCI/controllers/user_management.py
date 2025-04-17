from database.dao.factory.sql_dao_factory import SQLDAOFactory
from controllers.user_control import UserControl
from models.user import User
import hashlib
import logging
import os
from database.dao.profile_dao import ProfileDAO 


logger = logging.getLogger('gerenciador_usuarios')


class UserManagement:
    def __init__(self):
        factory = SQLDAOFactory()
        user_dao = factory.create_user_dao()
        self.user_control = UserControl(user_dao)
        self.profile_dao = ProfileDAO()  

    def validar_login(self, username, senha):
        try:
            todos = self.user_control.list_all()
            usuario = next((u for u in todos if u.email == username or u.name == username), None)
            if not usuario:
                return None

            if self._verificar_senha(usuario.password, senha):
                return usuario
            return None
        except Exception as e:
            logger.error(f"Erro ao validar login: {e}")
            return None

    def _verificar_senha(self, senha_hash, senha_texto):
        try:
            partes = senha_hash.split('$')
            if len(partes) != 4:
                return False

            algoritmo, iteracoes, salt, hash_armazenado = partes
            iteracoes = int(iteracoes)

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

    def adicionar_usuario(self, nome, email, senha, matricula):
        try:
            user = User(
                id=None,
                name=nome,
                email=email,
                password=self._gerar_hash_senha(senha),
                matricula=matricula
            )
            self.user_control.add(user)
            return user
        except Exception as e:
            logger.error(f"Erro ao adicionar usuário: {e}")
            return None

    def listar_usuarios(self):
        return self.user_control.list_all()

    def remover_usuario(self, user_id):
        try:
            self.user_control.delete(user_id)
            return True
        except Exception as e:
            logger.error(f"Erro ao remover usuário: {e}")
            return False
        
    def _gerar_hash_senha(self, senha_texto):
        try:
            algoritmo = 'sha256'
            salt = os.urandom(16).hex()
            iteracoes = 100000
            hash_gerado = hashlib.pbkdf2_hmac(
                algoritmo,
                senha_texto.encode('utf-8'),
                salt.encode('utf-8'),
                iteracoes
            ).hex()
            return f"{algoritmo}${iteracoes}${salt}${hash_gerado}"
        except Exception as e:
            logger.error(f"Erro ao gerar hash da senha: {e}")
            return senha_texto  # fallback inseguro (evite em produção)
