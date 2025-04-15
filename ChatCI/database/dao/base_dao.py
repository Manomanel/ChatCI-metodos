# base_dao.py
from typing import List, Dict, Any
from database.manager import DatabaseManager
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
    
    def _execute_update(self, query: str, params: tuple = None) -> int:
        connection = None
        cursor = None
        
        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            return cursor.rowcount
            
        except Exception as e:
            logger.error(f"Erro ao executar atualização: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.db_manager.release_connection(connection)
    
    def _execute_insert_returning_id(self, query: str, params: tuple = None) -> int:
        connection = None
        cursor = None
        
        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            id_gerado = cursor.fetchone()[0]
            connection.commit()
            return id_gerado
            
        except Exception as e:
            logger.error(f"Erro ao executar inserção: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.db_manager.release_connection(connection)