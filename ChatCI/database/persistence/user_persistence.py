from typing import List, Dict, Any, Optional
from .base_persistence import BasePersistence
import hashlib
import secrets
import logging
from datetime import datetime, timedelta

logger = logging.getLogger('user_dao')

class UserPersistence(BasePersistence):
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE username = %s"
        results = self._execute_query(query, (username,))
        return results[0] if results else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE email = %s"
        results = self._execute_query(query, (email,))
        return results[0] if results else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE id = %s"
        results = self._execute_query(query, (user_id,))
        return results[0] if results else None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM users ORDER BY id"
        return self._execute_query(query)
    
    # first_name: 20 caracteres
    # last_name: 30 caracteres
    # email: @ci.ufpb.br ou @academico.ufpb.br ou @di.ufpb.br
    # username: 15 caracteres max, 5 caracteres min; verificar se já existe na database; não pode ter número
    # password: 64 caracteres max, 10 caracteres min
    
    # Adicionar atributos na criação de usuários
    def create_user(self, username: str, email: str, password: str, first_name: str, 
                last_name: str, student: bool = True, professor: bool = False, 
                email_verified: bool = False, is_staff: bool = False, 
                is_superuser: bool = False) -> int:
        # Verifica se o usuário ou email já existem
        if self.get_user_by_username(username):
            raise ValueError(f"Usuário com username '{username}' já existe")
        
        if self.get_user_by_email(email):
            raise ValueError(f"Usuário com email '{email}' já existe")
        
        # Gerar token de verificação se o email não foi verificado
        verification_token = None
        token_expires = None
        
        if not email_verified:
            verification_token = secrets.token_urlsafe(32)
            token_expires = datetime.now() + timedelta(days=1)
        
        # Hash da senha
        salt = secrets.token_hex(8)
        hashed_password = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            150000
        ).hex()
        
        django_password = f"pbkdf2_sha256$150000${salt}${hashed_password}"
        
        query = """
        INSERT INTO users (
            username, email, password, first_name, last_name, 
            student, professor, email_verified, is_staff, is_superuser,
            verification_token, token_expires
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
        """
        
        params = (
            username, email, django_password, first_name, last_name,
            student, professor, email_verified, is_staff, is_superuser,
            verification_token, token_expires
        )
        
        return self._execute_insert_returning_id(query, params)

    def update_user(self, user_id: int, **fields) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Se estiver atualizando username ou email, verificar se já existem
        if 'username' in fields and fields['username'] != user['username']:
            if self.get_user_by_username(fields['username']):
                raise ValueError(f"Usuário com username '{fields['username']}' já existe")
        
        if 'email' in fields and fields['email'] != user['email']:
            if self.get_user_by_email(fields['email']):
                raise ValueError(f"Usuário com email '{fields['email']}' já existe")
        
        # Se estiver atualizando a senha, hashear
        if 'password' in fields:
            salt = secrets.token_hex(8)
            hashed_password = hashlib.pbkdf2_hmac(
                'sha256', 
                fields['password'].encode('utf-8'), 
                salt.encode('utf-8'), 
                150000
            ).hex()
            
            fields['password'] = f"pbkdf2_sha256$150000${salt}${hashed_password}"

        set_clauses = []
        params = []
        
        for field, value in fields.items():
            set_clauses.append(f"{field} = %s")
            params.append(value)
        
        params.append(user_id) 
        
        query = f"""
        UPDATE users 
        SET {', '.join(set_clauses)} 
        WHERE id = %s
        """
        
        rows_affected = self._execute_update(query, tuple(params))
        return rows_affected > 0
    
    def verify_email(self, token: str) -> bool:
        """
        Verifica o email de um usuário usando um token
        
        Args:
            token: Token de verificação
            
        Returns:
            True se o email foi verificado, False caso contrário
        """
        # Buscar usuário pelo token
        query = """
        SELECT id FROM users 
        WHERE verification_token = %s 
        AND token_expires > CURRENT_TIMESTAMP
        """
        
        results = self._execute_query(query, (token,))
        
        if not results:
            return False
        
        # Atualizar usuário
        user_id = results[0]['id']
        update_query = """
        UPDATE users 
        SET email_verified = TRUE, verification_token = NULL, token_expires = NULL 
        WHERE id = %s
        """
        
        rows_affected = self._execute_update(update_query, (user_id,))
        return rows_affected > 0
    
    def create_superuser(self, username: str, email: str, password: str, 
                    first_name: str, last_name: str) -> int:
        """
        Cria um superusuário (admin)
        
        Args:
            username: Nome de usuário
            email: Email
            password: Senha
            first_name: Primeiro nome
            last_name: Sobrenome
            
        Returns:
            ID do superusuário criado
        """
        return self.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            student=False,
            professor=True,
            email_verified=True,
            is_staff=True,
            is_superuser=True
        )
    
    def _execute_insert_returning_id(self, query: str, params: tuple = None) -> int:
        connection = None
        cursor = None
        
        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            id_gerado = cursor.fetchone()[0]
            connection.commit()
            return id_gerado
            
        except Exception as e:
            logger.error(f"Erro ao executar inserção: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.db_manager.release_connection(connection)