from typing import List, Dict, Any, Optional
from database.dao.base_dao import BaseDAO
import hashlib
import secrets
import logging

logger = logging.getLogger('user_dao')

class UserDAO(BaseDAO):
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
    
    def create_user(self, username: str, email: str, password: str, first_name: str, 
                   last_name: str, student: bool = True, professor: bool = False) -> int:
        # Verificar se o usuário ou email já existem
        if self.get_user_by_username(username):
            raise ValueError(f"Usuário com username '{username}' já existe")
        
        if self.get_user_by_email(email):
            raise ValueError(f"Usuário com email '{email}' já existe")
        
        # Hash da senha
        salt = secrets.token_hex(8)
        hashed_password = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            150000
        ).hex()
        
        # Formato compatível com Django
        django_password = f"pbkdf2_sha256$150000${salt}${hashed_password}"
        
        query = """
        INSERT INTO users (
            username, email, password, first_name, last_name, student, professor
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
        """
        
        params = (
            username, email, django_password, first_name, last_name, student, professor
        )
        
        return self._execute_insert_returning_id(query, params)