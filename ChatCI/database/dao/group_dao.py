from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class GroupDAO(ABC):
    @abstractmethod
    def create_group(self, name: str, description: str = "") -> int:
        pass
    
    @abstractmethod
    def get_group_by_id(self, group_id: int) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_group_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_all_groups(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def add_member(self, group_id: int, user_id: int) -> bool:
        pass
    
    @abstractmethod
    def remove_member(self, group_id: int, user_id: int) -> bool:
        pass
    
    @abstractmethod
    def is_member(self, group_id: int, user_id: int) -> bool:
        pass
    
    @abstractmethod
    def is_banned(self, group_id: int, user_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_user_groups(self, user_id: int) -> List[Dict[str, Any]]:
        pass