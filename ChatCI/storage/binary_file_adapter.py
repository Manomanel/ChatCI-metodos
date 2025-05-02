from interface.file_storage import FileStorage
from persistence.binary_file_persistence import BinaryFilePersistence

class BinaryFileAdapter(FileStorage):
    """
    Adaptador que converte arquivos genéricos em arquivos binários 
    e os salva usando a persistência de arquivos binários.
    """
    def __init__(self):
        # Instancia a própria persistência internamente
        self._binary_file_dao = BinaryFilePersistence()

    def salva_arquivo_adaptado(self, file_name: str, data: bytes) -> int:
        """
        Adapta e salva um arquivo genérico como arquivo binário.

        Args:
            file_name: Nome do arquivo
            data: Conteúdo binário

        Returns:
            ID do arquivo salvo no banco de dados
        """
        return self._binary_file_dao.save_file(file_name, data)

    def recupera_arquivo_adaptado(self, file_id: int) -> dict | None:
        """
        Recupera e adapta um arquivo binário para formato genérico.

        Args:
            file_id: ID do arquivo a recuperar

        Returns:
            Dicionário com 'file_name' e 'file_data' ou None
        """
        return self._binary_file_dao.get_file_by_id(file_id)