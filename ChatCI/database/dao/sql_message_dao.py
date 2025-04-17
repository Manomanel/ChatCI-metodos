from typing import List, Optional
from models.message import Message
from .interfaces.message_dao import MessageDAO

class SQLMessageDAO(MessageDAO):
    def __init__(self):
        self.messages: List[Message] = []
        self._id_counter = 1

    def save_msg(self, msg: Message) -> None:
        msg.id = self._id_counter
        self.messages.append(msg)
        self._id_counter += 1

    def find_by_id(self, msg_id: int) -> Optional[Message]:
        for msg in self.messages:
            if msg.id == msg_id:
                return msg
        return None

    def delete_msg(self, msg_id: int) -> None:
        self.messages = [msg for msg in self.messages if msg.id != msg_id]

    def list_all_user_msgs(self, user_id: int) -> List[Message]:
        return [msg for msg in self.messages if msg.sender == str(user_id)]

    def list_all(self) -> List[Message]:
        return self.messages
