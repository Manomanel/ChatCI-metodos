from .dao_factory import DAOFactory
from ..interfaces.user_dao import UserDAO
from ..interfaces.message_dao import MessageDAO
from ..sql_user_dao import SQLUserDAO
from ..sql_message_dao import SQLMessageDAO  # podemos criar depois

class SQLDAOFactory(DAOFactory):
    def create_user_dao(self) -> UserDAO:
        return SQLUserDAO()

    def create_message_dao(self) -> MessageDAO:
        return SQLMessageDAO()
