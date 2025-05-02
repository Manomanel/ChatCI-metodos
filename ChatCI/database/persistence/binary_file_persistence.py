from typing import Optional
from dao.binary_file_dao import BinaryFileDAO
from .base_persistence import BasePersistence
import logging

logger = logging.getLogger('binary_file_persistence')

class BinaryFilePersistence(BasePersistence, BinaryFileDAO):
    """Classe de persistência para manipulação de arquivos binários usando a interface BinaryFileDAO"""
    
    def save_file(self, file_name: str, file_data: bytes) -> int:
        """
        Salva um arquivo binário no banco de dados.
        
        Args:
            file_name: Nome do arquivo
            file_data: Dados binários do arquivo
        
        Returns:
            ID do arquivo salvo
        """
        query = """
        INSERT INTO files (file_name, file_data)
        VALUES (%s, %s)
        RETURNING file_id
        """
        
        try:
            # Executa a query para inserir o arquivo e retornar o ID
            return self._execute_insert_returning_id(query, (file_name, file_data))
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo binário: {e}")
            return -1

    def get_file_by_id(self, file_id: int) -> Optional[dict]:
        """
        Recupera os dados de um arquivo binário pelo ID.
        
        Args:
            file_id: ID do arquivo
        
        Returns:
            Dados do arquivo como dicionário, ou None se não encontrado
        """
        query = """
        SELECT file_name, file_data
        FROM files
        WHERE file_id = %s
        """
        
        try:
            # Executa a query para recuperar os dados do arquivo
            results = self._execute_query(query, (file_id,))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Erro ao recuperar arquivo binário: {e}")
            return None