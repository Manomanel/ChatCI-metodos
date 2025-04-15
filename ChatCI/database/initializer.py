from database.manager import DatabaseManager
import logging
import hashlib
import json
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('db_initializer')

class DatabaseInitializer:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self._ensure_migration_table_exists()
    
    def _ensure_migration_table_exists(self):
        query = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) NOT NULL UNIQUE,
            migration_hash VARCHAR(64) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) NOT NULL
        )
        """
        self._execute_query(query)
        logger.info("Tabela de migrações verificada/criada com sucesso")
    
    def _execute_query(self, query: str, params: tuple = None) -> int:
        connection = None
        cursor = None
        
        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            return cursor.rowcount
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Erro ao executar query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.db_manager.release_connection(connection)
    
    def initialize_database(self) -> bool:
        """Inicializa o banco de dados com a tabela de usuários"""
        migrations = [
            {
                "name": "001_create_users_table",
                "queries": [
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(150) NOT NULL UNIQUE,
                        email VARCHAR(254) NOT NULL UNIQUE,
                        password VARCHAR(128) NOT NULL,
                        first_name VARCHAR(50) NOT NULL,
                        last_name VARCHAR(150) NOT NULL,
                        student BOOLEAN NOT NULL DEFAULT TRUE,
                        professor BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                ]
            },
            {
                "name": "002_create_profile_table",
                "queries": [
                    """
                    CREATE TABLE IF NOT EXISTS profile (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        bio TEXT NOT NULL DEFAULT '',
                        profile_picture VARCHAR(100) NULL
                    )
                    """
                ]
            },
            {
                "name": "003_create_event_table",
                "queries": [
                    """
                    CREATE TABLE IF NOT EXISTS event (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        description TEXT NOT NULL,
                        link VARCHAR(255) NOT NULL DEFAULT '',
                        event_date DATE NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                ]
            },
            
        ]
        
        success = True
        for migration in migrations:
            if not self.apply_migration(migration["name"], migration["queries"]):
                success = False
        
        return success
    
    def apply_migration(self, name: str, queries: List[str], force: bool = False) -> bool:
        """
        Aplica uma migração ao banco de dados
        
        Args:
            name: Nome da migração
            queries: Lista de queries SQL a serem executadas
            force: Se True, aplica a migração mesmo que já tenha sido aplicada antes
            
        Returns:
            True se a migração foi aplicada com sucesso, False caso contrário
        """
        # Verificar se a migração já foi aplicada
        if not force and self._migration_exists(name):
            logger.info(f"Migração {name} já foi aplicada anteriormente")
            return True

        content = json.dumps(queries)
        content_hash = self._calculate_hash(content)

        connection = None
        cursor = None
        
        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor()

            for query in queries:
                logger.info(f"Executando query: {query[:100]}...")
                cursor.execute(query)
            
            # Registrar migração
            cursor.execute(
                """
                INSERT INTO schema_migrations (migration_name, migration_hash, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (migration_name) 
                DO UPDATE SET migration_hash = %s, applied_at = CURRENT_TIMESTAMP, status = %s
                """,
                (name, content_hash, 'success', content_hash, 'success')
            )
            
            # Commit da transação
            connection.commit()
            logger.info(f"Migração {name} aplicada com sucesso")
            return True
            
        except Exception as e:
            if connection:
                connection.rollback()

            try:
                self._register_migration(name, content_hash, 'failed')
            except:
                pass
                
            logger.error(f"Erro ao aplicar migração {name}: {e}")
            return False
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.db_manager.release_connection(connection)
    
    def _calculate_hash(self, content: str) -> str:
        """Calcula o hash SHA-256 do conteúdo da migração"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _register_migration(self, name: str, content_hash: str, status: str = 'success') -> bool:
        """Registra uma migração na tabela de controle"""
        query = """
        INSERT INTO schema_migrations (migration_name, migration_hash, status)
        VALUES (%s, %s, %s)
        ON CONFLICT (migration_name) 
        DO UPDATE SET migration_hash = %s, applied_at = CURRENT_TIMESTAMP, status = %s
        """
        try:
            self._execute_query(query, (name, content_hash, status, content_hash, status))
            return True
        except Exception as e:
            logger.error(f"Erro ao registrar migração {name}: {e}")
            return False