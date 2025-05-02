from abc import ABC, abstractmethod
from typing import Optional

class BinaryFileDAO(ABC):
    """Interface DAO para manipulação de arquivos binários"""
    
    @abstractmethod
    def save_file(self, file_name: str, file_data: bytes) -> int:
        """
        Salva um arquivo binário no banco de dados
        
        Args:
            file_name: Nome do arquivo
            file_data: Dados binários do arquivo
        
        Returns:
            ID do arquivo salvo
        """
        pass
    
    @abstractmethod
    def get_file_by_id(self, file_id: int) -> Optional[dict]:
        """
        Recupera os dados de um arquivo binário pelo ID
        
        Args:
            file_id: ID do arquivo
        
        Returns:
            Dados do arquivo como dicionário, ou None se não encontrado
        """
        pass