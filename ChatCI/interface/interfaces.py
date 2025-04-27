from abc import ABC, abstractmethod

class IMediator(ABC):
    @abstractmethod
    def notify(self, event: str, data: dict = None) -> any:
        pass
    
class ICommand(ABC):
    @abstractmethod
    def execute(self) -> any:
        pass
    
class IComponent(ABC):
    def __init__(self):
        self.mediator = None
    
    def set_mediator(self, mediator: IMediator):
        self.mediator = mediator
