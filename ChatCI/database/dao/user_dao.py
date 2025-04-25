from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class UserDAO(ABC):
    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_all_users(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_user(self, username: str, email: str, password: str, first_name: str, 
                    last_name: str, student: bool = True, professor: bool = False, 
                    email_verified: bool = False, is_staff: bool = False, 
                    is_superuser: bool = False) -> int:
        pass

    @abstractmethod
    def update_user(self, user_id: int, **fields) -> bool:
        pass

    @abstractmethod
    def verify_email(self, token: str) -> bool:
        pass

    @abstractmethod
    def create_superuser(self, username: str, email: str, password: str, 
                        first_name: str, last_name: str) -> int:
        pass