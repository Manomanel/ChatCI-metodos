# profile_dao.py
from typing import Dict, Any, Optional
from database.dao.base_dao import BaseDAO
import logging

logger = logging.getLogger('profile_dao')

class ProfileDAO(BaseDAO):
    """DAO para manipulação da tabela de perfis de usuários"""
    def create(self, user_id: int, bio: str = "", profile_picture: str = None) -> int:
        """
        Cria um novo perfil para um usuário
        
        Args:
            user_id: ID do usuário
            bio: Biografia do usuário
            profile_picture: Caminho para a foto de perfil
            
        Returns:
            ID do perfil criado
        """
        
        query = """
        INSERT INTO profile (user_id, bio, profile_picture)
        VALUES (%s, %s, %s)
        RETURNING id
        """
        
        return self._execute_insert_returning_id(query, (user_id, bio, profile_picture))

    def get_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Busca o perfil pelo ID do usuário"""
        query = "SELECT * FROM profile WHERE user_id = %s"
        results = self._execute_query(query, (user_id,))
        return results[0] if results else None

    def update(self, user_id: int, bio: str = None, profile_picture: str = None) -> bool:
        """
        Atualiza o perfil de um usuário
        
        Args:
            user_id: ID do usuário
            bio: Nova biografia
            profile_picture: Novo caminho para a foto de perfil
            
        Returns:
            True se o perfil foi atualizado, False caso contrário
        """
        profile = self.get_by_user_id(user_id)
        if not profile:
            return False
        
        set_clauses = []
        params = []
        
        if bio is not None:
            set_clauses.append("bio = %s")
            params.append(bio)
            
        if profile_picture is not None:
            set_clauses.append("profile_picture = %s")
            params.append(profile_picture)
            
        if not set_clauses:
            return True  
            
        params.append(user_id) 
        
        query = f"""
        UPDATE profile 
        SET {', '.join(set_clauses)} 
        WHERE user_id = %s
        """
        
        rows_affected = self._execute_update(query, tuple(params))
        return rows_affected > 0