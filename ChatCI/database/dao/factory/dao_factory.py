from abc import ABC, abstractmethod
from database.dao.interfaces.user_dao import UserDAO
from database.dao.interfaces.message_dao import MessageDAO  # quando for criar


class DAOFactory(ABC):
    @abstractmethod
    def create_user_dao(self) -> UserDAO:
        pass

    @abstractmethod
    def create_message_dao(self) -> MessageDAO:
        pass
