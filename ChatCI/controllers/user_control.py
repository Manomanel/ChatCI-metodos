from database.dao.interfaces.user_dao import UserDAO
from models.user import User
from typing import List, Dict

class UserControl:
    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    def add(self, user: User) -> None:
        self.user_dao.save(user)

    def list_all(self) -> List[User]:
        return self.user_dao.list_all()

    def get_config(self, user_id: int) -> Dict:
        return self.user_dao.user_configs(user_id)

    def set_config(self, user_id: int, configs: Dict) -> None:
        self.user_dao.set_user_configs(user_id, configs)

    def delete(self, user_id: int) -> None:
        self.user_dao.delete(user_id)
