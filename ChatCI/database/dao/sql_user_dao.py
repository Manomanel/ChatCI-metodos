from typing import Dict, List, Optional
from models.user import User  # ajustar conforme o local real
from .interfaces.user_dao import UserDAO

class SQLUserDAO(UserDAO):
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.user_configs_map: Dict[int, Dict] = {}
        self._id_counter = 1

    def save(self, user: User) -> None:
        user.id = self._id_counter
        self.users[self._id_counter] = user
        self._id_counter += 1

    def find_by_id(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)

    def list_all(self) -> List[User]:
        return list(self.users.values())

    def delete(self, user_id: int) -> None:
        if user_id in self.users:
            del self.users[user_id]

    def user_configs(self, user_id: int) -> Dict:
        return self.user_configs_map.get(user_id, {})

    def set_user_configs(self, user_id: int, configs: Dict) -> None:
        self.user_configs_map[user_id] = configs
