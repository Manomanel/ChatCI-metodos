from database.dao.user_dao import  UserDAO
from typing import Dict, Any, List
from ChatCI.database.persistence.user_persistence import UserPersistence

class UserControl:
    def __init__(self, users: Dict[str, Any]):
        self.user = users
        self.userDAO: UserDAO = UserPersistence()