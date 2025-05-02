from abc import ABC, abstractmethod
from typing import Optional

class BinaryFileDAO(ABC):
    @abstractmethod
    def save_file(self, file_name: str, file_data: bytes) -> int:
        pass
    
    @abstractmethod
    def get_file_by_id(self, file_id: int) -> Optional[dict]:
        pass