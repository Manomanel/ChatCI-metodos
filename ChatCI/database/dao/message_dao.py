from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class MessageDAO(ABC):
    @abstractmethod
    def create_message(self, group_id: int, user_id: int, text: str, file: str = None) -> int:
        pass
    
    @abstractmethod
    def get_group_messages(self, group_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        pass