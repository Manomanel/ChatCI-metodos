from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ProfileDAO(ABC):
    @abstractmethod
    def create(self, user_id: int, bio: str = "", profile_picture: str = None) -> int:
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def update(self, user_id: int, bio: str = None, profile_picture: str = None) -> bool:
        pass