from typing import List, Dict, Any, Optional
from .base_persistence import BasePersistence
import logging
from datetime import datetime

logger = logging.getLogger('message_dao')

class MessagePersistence(BasePersistence):
    """DAO para manipulação da tabela de mensagens"""
    
    def create_message(self, group_id: int, user_id: int, text: str, file: str = None) -> int:
        """
        Cria uma nova mensagem em um grupo
        
        Args:
            group_id: ID do grupo
            user_id: ID do usuário que enviou a mensagem
            text: Conteúdo da mensagem
            file: Caminho para arquivo anexo (opcional)
            
        Returns:
            ID da mensagem criada
        """
        query = """
        INSERT INTO messages (group_id, user_id, text, file)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        return self._execute_insert_returning_id(query, (group_id, user_id, text, file))
    
    def get_group_messages(self, group_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Busca mensagens de um grupo com paginação
        
        Args:
            group_id: ID do grupo
            limit: Número máximo de mensagens a retornar
            offset: Número de mensagens a pular
            
        Returns:
            Lista de mensagens
        """
        query = """
        SELECT m.*, u.username, u.first_name, u.last_name 
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.group_id = %s
        ORDER BY m.created_at DESC
        LIMIT %s OFFSET %s
        """
        return self._execute_query(query, (group_id, limit, offset))