from datetime import datetime
from typing import Optional

class Message:
    def __init__(self, id: int, content: str, sender: str, group: str,
                 date_time: Optional[datetime] = None, attached_file: Optional[str] = None):
        self.id = id
        self.content = content
        self.sender = sender
        self.group = group
        self.date_time = date_time or datetime.now()
        self.attached_file = attached_file
