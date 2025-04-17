from abc import ABC, abstractmethod
from typing import List, Optional
from models.message import Message  # ajuste esse caminho se necessário

class MessageDAO(ABC):
    @abstractmethod
    def save_msg(self, msg: Message) -> None:
        pass

    @abstractmethod
    def find_by_id(self, msg_id: int) -> Optional[Message]:
        pass

    @abstractmethod
    def delete_msg(self, msg_id: int) -> None:
        pass

    @abstractmethod
    def list_all_user_msgs(self, user_id: int) -> List[Message]:
        pass

    @abstractmethod
    def list_all(self) -> List[Message]:
        pass
