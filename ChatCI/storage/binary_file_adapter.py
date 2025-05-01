from entities.arquivo_binario import ArquivoBinario
from database.persistence.base_persistence import BasePersistence
from storage.file_storage import FileStorage
import logging

logger = logging.getLogger('binary_file_adapter')

class BinaryFileAdapter(BasePersistence, FileStorage):
    def __init__(self):
        super().__init__()  # Chama o construtor da classe BasePersistence

    def saveFile(self, arquivo: ArquivoBinario) -> bool:
        """
        Salva um arquivo binário no banco de dados.
        
        Args:
            arquivo: O objeto ArquivoBinario que contém o arquivo e os dados.
        
        Returns:
            True se o arquivo foi salvo com sucesso, False caso contrário.
        """
        query = """
        INSERT INTO files (file_name, file_data)
        VALUES (%s, %s)
        RETURNING file_id
        """
        
        try:
            # Executa a query de inserção no banco de dados e recupera o ID do arquivo
            file_id = self._execute_insert_returning_id(query, (arquivo.file_name, arquivo.file_data))
            return file_id > 0  # Verifica se o arquivo foi salvo com sucesso
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo binário: {e}")
            return False

    def getFile(self, file_id: int) -> ArquivoBinario:
        """
        Recupera um arquivo binário do banco de dados.
        
        Args:
            file_id: ID do arquivo.
        
        Returns:
            ArquivoBinario com os dados do arquivo.
        """
        query = """
        SELECT file_name, file_data
        FROM files
        WHERE file_id = %s
        """
        
        try:
            # Executa a query para recuperar os dados binários do arquivo
            results = self._execute_query(query, (file_id,))
            if results:
                file_data = results[0]["file_data"]
                file_name = results[0]["file_name"]
                return ArquivoBinario(file_data, file_name)
            else:
                return None
        except Exception as e:
            logger.error(f"Erro ao recuperar arquivo binário: {e}")
            return None