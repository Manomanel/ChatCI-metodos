from typing import List, Dict, Any, Optional
from .base_persistence import BasePersistence
import logging
from ..dao.group_dao import GroupDAO

logger = logging.getLogger('group_dao')

class GroupPersistence(BasePersistence, GroupDAO):
    """DAO para manipulação da tabela de grupos"""
    
    def create_group(self, name: str, description: str = "") -> int:
        """
        Cria um novo grupo
        
        Args:
            name: Nome do grupo
            description: Descrição do grupo
            
        Returns:
            ID do grupo criado
        """
        query = """
        INSERT INTO groups (name, description)
        VALUES (%s, %s)
        RETURNING id
        """
        return self._execute_insert_returning_id(query, (name, description))
    
    def get_group_by_id(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Busca um grupo pelo ID"""
        query = "SELECT * FROM groups WHERE id = %s"
        results = self._execute_query(query, (group_id,))
        return results[0] if results else None
    
    def get_group_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Busca um grupo pelo nome"""
        query = "SELECT * FROM groups WHERE name = %s"
        results = self._execute_query(query, (name,))
        return results[0] if results else None
    
    def get_all_groups(self) -> List[Dict[str, Any]]:
        """Busca todos os grupos"""
        query = "SELECT * FROM groups ORDER BY name"
        return self._execute_query(query)
    
    def add_member(self, group_id: int, user_id: int) -> bool:
        """
        Adiciona um membro a um grupo
        
        Args:
            group_id: ID do grupo
            user_id: ID do usuário
            
        Returns:
            True se o membro foi adicionado, False caso contrário
        """
        try:
            query = """
            INSERT INTO groups_members (group_id, user_id)
            VALUES (%s, %s)
            """
            rows_affected = self._execute_update(query, (group_id, user_id))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Erro ao adicionar membro ao grupo: {e}")
            return False
        
    def remove_member(self, group_id: int, user_id: int) -> bool:
        """
        Remove um membro de um grupo
        
        Args:
            group_id: ID do grupo
            user_id: ID do usuário
            
        Returns:
            True se o membro foi removido, False caso contrário
        """
        query = """
        DELETE FROM groups_members 
        WHERE group_id = %s AND user_id = %s
        """
        rows_affected = self._execute_update(query, (group_id, user_id))
        return rows_affected > 0
    
    def is_member(self, group_id: int, user_id: int) -> bool:
        """
        Verifica se um usuário é membro de um grupo
        
        Args:
            group_id: ID do grupo
            user_id: ID do usuário
            
        Returns:
            True se o usuário é membro, False caso contrário
        """
        query = """
        SELECT COUNT(*) as count
        FROM groups_members
        WHERE group_id = %s AND user_id = %s
        """
        result = self._execute_query(query, (group_id, user_id))
        return result[0]['count'] > 0 if result else False
    
    def is_banned(self, group_id: int, user_id: int) -> bool:
        """
        Verifica se um usuário está banido de um grupo
        
        Args:
            group_id: ID do grupo
            user_id: ID do usuário
            
        Returns:
            True se o usuário está banido, False caso contrário
        """
        query = """
        SELECT COUNT(*) as count
        FROM groups_banned_members
        WHERE group_id = %s AND user_id = %s
        """
        result = self._execute_query(query, (group_id, user_id))
        return result[0]['count'] > 0 if result else False
    
    def get_user_groups(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Retorna todos os grupos que um usuário participa
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de grupos que o usuário participa
        """
        query = """
        SELECT g.* 
        FROM groups g
        JOIN groups_members gm ON g.id = gm.group_id
        WHERE gm.user_id = %s
        ORDER BY g.name
        """
        return self._execute_query(query, (user_id,))
    
    def ban_user(self, group_id: int, user_id: int) -> bool:
        """
        Adiciona um usuário à lista de banidos de um grupo
        
        Args:
            group_id: ID do grupo
            user_id: ID do usuário
            
        Returns:
            True se o usuário foi banido, False caso contrário
        """
        try:
            # Remove o usuário do grupo, se for membro
            if self.is_member(group_id, user_id):
                self.remove_member(group_id, user_id)
            
            # Adiciona à lista de banidos
            query = """
            INSERT INTO groups_banned_members (group_id, user_id)
            VALUES (%s, %s)
            """
            rows_affected = self._execute_update(query, (group_id, user_id))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Erro ao banir usuário: {e}")
            return False

    def unban_user(self, group_id: int, user_id: int) -> bool:
        """
        Remove um usuário da lista de banidos de um grupo
        
        Args:
            group_id: ID do grupo
            user_id: ID do usuário
            
        Returns:
            True se o usuário foi desbanido, False caso contrário
        """
        try:
            query = """
            DELETE FROM groups_banned_members 
            WHERE group_id = %s AND user_id = %s
            """
            rows_affected = self._execute_update(query, (group_id, user_id))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Erro ao desbanir usuário: {e}")
            return False

    def get_group_members(self, group_id: int) -> List[Dict[str, Any]]:
        """
        Retorna todos os membros de um grupo
        
        Args:
            group_id: ID do grupo
            
        Returns:
            Lista de membros do grupo
        """
        query = """
        SELECT u.id, u.username, u.first_name, u.last_name, u.email
        FROM users u
        JOIN groups_members gm ON u.id = gm.user_id
        WHERE gm.group_id = %s
        ORDER BY u.username
        """
        return self._execute_query(query, (group_id,))

    def get_banned_members(self, group_id: int) -> List[Dict[str, Any]]:
        """
        Retorna todos os usuários banidos de um grupo
        
        Args:
            group_id: ID do grupo
            
        Returns:
            Lista de usuários banidos do grupo
        """
        query = """
        SELECT u.id, u.username, u.first_name, u.last_name, u.email
        FROM users u
        JOIN groups_banned_members gbm ON u.id = gbm.user_id
        WHERE gbm.group_id = %s
        ORDER BY u.username
        """
        return self._execute_query(query, (group_id,))