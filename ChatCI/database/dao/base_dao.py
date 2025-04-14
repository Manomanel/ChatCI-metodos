from typing import List, Dict, Any
from ChatCI.database.manager import DatabaseManager
import logging

logger = logging.getLogger('base_dao')
class BaseDAO:
    """Classe base para todos os DAOs com métodos comuns"""
    def __init__(self):
        self.db_manager = DatabaseManager()
        
    def _execute_query(self, query: str, params: tuple = None) -> List[Dict[str,Any]]:
        """Executa uma consulta SQL e retorna os resultados"""
        connection = None
        cursor = None
        results = []
        
        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            
            if cursor.description:
                columns_names = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    results.append(dict(zip(columns_names, row)))
            return results
        
        except Exception as e:
            logger.error(f"Erro ao executar a consulta: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.db_manager.release_connection(connection)