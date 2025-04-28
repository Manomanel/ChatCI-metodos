from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date

class EventDAO(ABC):
    @abstractmethod
    def create_event(self, title: str, description: str, link: str = "", event_date: date = None) -> int:
        pass
    
    @abstractmethod
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_events_by_title(self, title: str) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_all_events(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_upcoming_events(self, limit: int = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_past_events(self, limit: int = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def update_event(self, event_id: int, title: str = None, description: str = None, 
                    link: str = None, event_date: date = None) -> bool:
        pass
    
    @abstractmethod
    def delete_event(self, event_id: int) -> bool:
        pass