from typing import Dict, Any, Optional
from .base_persistence import BasePersistence
import logging
from ..dao.profile_dao import ProfileDAO

logger = logging.getLogger('profile_dao')

class ProfilePersistence(BasePersistence, ProfileDAO):
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
    

    #CLASSE ORIGINADORA DO MEMENTO, O MEMENTO É A TABELA PROFILE HISTORY DA DB
    def save_memento(self, user_id: int) -> bool:
        #Salva o perfil atual como um memento no banco de dados
        profile = self.get_by_user_id(user_id)
        if not profile:
            return False
        
        query = """
        INSERT INTO profile_history (user_id, bio, profile_picture)
        VALUES (%s, %s, %s)
        """

        self._execute_insert_returning_id(query, (
            profile['user_id'],
            profile.get('bio'),
            profile.get('profile_picture')
        ))

    def restore_last_memento(self, user_id: int) -> bool:
        query = """
        SELECT bio, profile_picture
        FROM profile_history
        WHERE user_id = %s
        ORDER BY saved_at DESC
        LIMIT 1
        """
        resultados = self._execute_query(query, (user_id,))
        if not resultados:
            return False
        
        ultimo_estado = resultados[0]
        return self.update(
            user_id,
            bio = ultimo_estado.get("bio"),
            profile_picture = ultimo_estado.get("profile_picture")
        )