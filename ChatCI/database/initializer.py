from database.manager import DatabaseManager
import logging

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
            }
        ]
        
        success = True
        for migration in migrations:
            if not self.apply_migration(migration["name"], migration["queries"]):
                success = False
        
        return success
    
    def apply_migration(self, name: str, queries: list) -> bool:
        connection = None
        cursor = None
        
        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor()
            
            # Verificar se a migração já foi aplicada
            cursor.execute(
                "SELECT COUNT(*) FROM schema_migrations WHERE migration_name = %s AND status = 'success'",
                (name,)
            )
            count = cursor.fetchone()[0]
            if count > 0:
                logger.info(f"Migração {name} já foi aplicada anteriormente")
                return True
            
            # Executar queries
            for query in queries:
                logger.info(f"Executando query: {query[:100]}...")
                cursor.execute(query)
            
            # Registrar migração
            cursor.execute(
                """
                INSERT INTO schema_migrations (migration_name, migration_hash, status)
                VALUES (%s, %s, %s)
                """,
                (name, "initial_hash", "success")
            )
            
            # Commit da transação
            connection.commit()
            logger.info(f"Migração {name} aplicada com sucesso")
            return True
            
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Erro ao aplicar migração {name}: {e}")
            return False
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.db_manager.release_connection(connection)