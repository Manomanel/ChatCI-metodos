from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from models.user import User  # ajuste conforme a localização real

class UserDAO(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def list_all(self) -> List[User]:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        pass

    @abstractmethod
    def user_configs(self, user_id: int) -> Dict:
        pass

    @abstractmethod
    def set_user_configs(self, user_id: int, configs: Dict) -> None:
        pass
