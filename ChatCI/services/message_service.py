from typing import List, Dict, Any, Optional
from database.persistence.message_persistence import MessagePersistence
from database.persistence.group_persistence import GroupPersistence
from database.factory.user_dao_factory import UserDAOFactory
import logging

logger = logging.getLogger('message_service')

class MessageService:
    """Serviço simplificado para gerenciamento de mensagens"""
    
    def __init__(self):
        self.message_dao = MessagePersistence()
        self.group_dao = GroupPersistence()
        self.user_dao = UserDAOFactory.get_instance()
    
    def send_message_to_group(self, group_id: int, user_id: int, text: str) -> int:
        """Envia uma mensagem para um grupo"""
        if not self.group_dao.is_member(group_id, user_id):
            logger.warning(f"Usuário {user_id} não é membro do grupo {group_id}")
            return None

        if self.group_dao.is_banned(group_id, user_id):
            logger.warning(f"Usuário {user_id} está banido do grupo {group_id}")
            return None
        
        return self.message_dao.create_message(group_id, user_id, text)
    
    def send_group_welcome_message(self, group_id: int):
        """Envia mensagem de boas-vindas para um novo grupo"""
        group = self.group_dao.get_group_by_id(group_id)
        if not group:
            logger.error(f"Grupo {group_id} não encontrado")
            return
        
        welcome_message = f"Bem-vindos ao grupo {group['name']}!"

        system_user_id = 1
        self.message_dao.create_message(group_id, system_user_id, welcome_message)