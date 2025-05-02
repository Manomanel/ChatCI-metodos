from abc import ABC, abstractmethod
from entities.arquivo_binario import ArquivoBinario
class FileStorage(ABC):
    @abstractmethod
    def saveFile(self, arquivo: 'ArquivoBinario') -> bool:
        pass

    @abstractmethod
    def getFile(self, file_id: int) -> 'ArquivoBinario':
        pass