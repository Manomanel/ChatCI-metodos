from datetime import datetime

class Messages:
    def __init__(self, id: int, content: str, dateTime: datetime, sender: str, group: int, attached: bool, file: None):
        self.id = id
        self.content = content 
        self.sender = sender
        self.group = group
        self.dateTime = dateTime
        self.attached = attached
        self.file = file