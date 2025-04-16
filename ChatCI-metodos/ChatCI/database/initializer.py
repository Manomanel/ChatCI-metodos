from database.manager import DatabaseManager
from typing import List, Dict, Any, Optional
import logging
import hashlib
import json
import os
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('db_migrations.log')
    ]
)
logger = logging.getLogger('db_initializer')

class DatabaseInitializer:
    """
    Classe responsável por inicializar e atualizar o esquema do banco de dados
    """
    def __init__(self):
        self.db_manager = DatabaseManager()
        self._ensure_migration_table_exists()
    
    def _ensure_migration_table_exists(self):
        """Cria a tabela de controle de migrações se não existir"""
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
        """Executa uma query SQL"""
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
    
    def _migration_exists(self, migration_name: str) -> bool:
        """Verifica se uma migração já foi aplicada"""
        connection = None
        cursor = None
        
        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM schema_migrations WHERE migration_name = %s AND status = 'success'",
                (migration_name,)
            )
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            logger.error(f"Erro ao verificar migração: {e}")
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
        
        # Calcular hash do conteúdo
        content = json.dumps(queries)
        content_hash = self._calculate_hash(content)
        
        # Iniciar transação
        connection = None
        cursor = None
        
        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor()
            
            # Executar queries
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
            
            # Registrar falha
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
    
    def initialize_database(self) -> bool:
        """
        Inicializa o banco de dados com todas as tabelas necessárias
        
        Returns:
            True se a inicialização foi bem-sucedida, False caso contrário
        """
        # Definir as migrações para criar as tabelas baseadas no modelo Django
        migrations = [
            {
                "name": "001_create_users_table",
                "queries": [
                    """
                    CREATE TABLE IF NOT EXISTS auth_group (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(150) NOT NULL UNIQUE
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS django_content_type (
                        id SERIAL PRIMARY KEY,
                        app_label VARCHAR(100) NOT NULL,
                        model VARCHAR(100) NOT NULL,
                        CONSTRAINT django_content_type_app_label_model_unique UNIQUE (app_label, model)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS auth_permission (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        content_type_id INTEGER NOT NULL REFERENCES django_content_type(id),
                        codename VARCHAR(100) NOT NULL,
                        CONSTRAINT auth_permission_content_type_id_codename_unique UNIQUE (content_type_id, codename)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS auth_group_permissions (
                        id SERIAL PRIMARY KEY,
                        group_id INTEGER NOT NULL REFERENCES auth_group(id),
                        permission_id INTEGER NOT NULL REFERENCES auth_permission(id),
                        CONSTRAINT auth_group_permissions_group_id_permission_id_unique UNIQUE (group_id, permission_id)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        password VARCHAR(128) NOT NULL,
                        last_login TIMESTAMP WITH TIME ZONE NULL,
                        username VARCHAR(150) NOT NULL UNIQUE,
                        email VARCHAR(254) NOT NULL UNIQUE,
                        first_name VARCHAR(50) NOT NULL,
                        last_name VARCHAR(150) NOT NULL,
                        student BOOLEAN NOT NULL DEFAULT TRUE,
                        professor BOOLEAN NOT NULL DEFAULT FALSE,
                        email_verified BOOLEAN NOT NULL DEFAULT FALSE,
                        is_staff BOOLEAN NOT NULL DEFAULT FALSE,
                        is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
                        verification_token VARCHAR(100) NULL UNIQUE,
                        token_expires TIMESTAMP WITH TIME ZONE NULL
                    )
                    """
                ]
            },
            {
                "name": "002_create_user_permissions",
                "queries": [
                    """
                    CREATE TABLE IF NOT EXISTS users_user_permissions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        permission_id INTEGER NOT NULL REFERENCES auth_permission(id),
                        CONSTRAINT users_user_permissions_user_id_permission_id_unique UNIQUE (user_id, permission_id)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS users_groups (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        group_id INTEGER NOT NULL REFERENCES auth_group(id),
                        CONSTRAINT users_groups_user_id_group_id_unique UNIQUE (user_id, group_id)
                    )
                    """
                ]
            },
            {
                "name": "003_create_coordinator_table",
                "queries": [
                    """
                    CREATE TABLE IF NOT EXISTS coordinator (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        curso VARCHAR(255) NOT NULL
                    )
                    """
                ]
            },
            {
                "name": "004_create_profile_table",
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
                "name": "005_create_event_table",
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
            {
                "name": "006_create_group_tables",
                "queries": [
                    """
                    CREATE TABLE IF NOT EXISTS group_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT NOT NULL DEFAULT '',
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS group_members (
                        id SERIAL PRIMARY KEY,
                        group_id INTEGER NOT NULL REFERENCES group_table(id) ON DELETE CASCADE,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        CONSTRAINT group_members_group_id_user_id_unique UNIQUE (group_id, user_id)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS group_banned_members (
                        id SERIAL PRIMARY KEY,
                        group_id INTEGER NOT NULL REFERENCES group_table(id) ON DELETE CASCADE,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        CONSTRAINT group_banned_members_group_id_user_id_unique UNIQUE (group_id, user_id)
                    )
                    """
                ]
            },
            {
                "name": "007_create_message_table",
                "queries": [
                    """
                    CREATE TABLE IF NOT EXISTS message (
                        id SERIAL PRIMARY KEY,
                        group_id INTEGER NOT NULL REFERENCES group_table(id) ON DELETE CASCADE,
                        text TEXT NOT NULL,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        file VARCHAR(100) NULL
                    )
                    """
                ]
            }
        ]
        
        # Aplicar migrações
        success = True
        for migration in migrations:
            if not self.apply_migration(migration["name"], migration["queries"]):
                success = False
        
        return success
    
    def run_update_script(self, script_name: str, script_content: str) -> bool:
        """
        Executa um script de atualização no banco
        
        Args:
            script_name: Nome do script para identificação
            script_content: Conteúdo SQL do script
            
        Returns:
            True se o script foi executado com sucesso, False caso contrário
        """
        # Dividir o script em queries individuais
        # Este é um método simples que assume que cada query termina com ponto e vírgula
        queries = [q.strip() for q in script_content.split(';') if q.strip()]
        
        # Usar o nome do script como nome da migração
        migration_name = f"update_{script_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return self.apply_migration(migration_name, queries)
    
    def add_column_if_not_exists(self, table: str, column: str, definition: str) -> bool:
        """
        Adiciona uma coluna a uma tabela se ela não existir
        
        Args:
            table: Nome da tabela
            column: Nome da coluna
            definition: Definição da coluna (tipo, constraints, etc)
            
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        migration_name = f"add_column_{table}_{column}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Query para verificar se a coluna existe
        check_query = f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = '{table}' AND column_name = '{column}'
            ) THEN
                ALTER TABLE {table} ADD COLUMN {column} {definition};
            END IF;
        END
        $$;
        """
        
        return self.apply_migration(migration_name, [check_query])
    
    def create_index_if_not_exists(self, table: str, columns: List[str], index_name: str = None) -> bool:
        """
        Cria um índice se ele não existir
        
        Args:
            table: Nome da tabela
            columns: Lista de colunas para o índice
            index_name: Nome do índice (opcional)
            
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        # Gerar nome do índice se não fornecido
        if not index_name:
            index_name = f"idx_{table}_{'_'.join(columns)}"
        
        migration_name = f"create_index_{index_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Query para criar o índice se não existir
        create_index_query = f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_indexes
                WHERE indexname = '{index_name}'
            ) THEN
                CREATE INDEX {index_name} ON {table} ({', '.join(columns)});
            END IF;
        END
        $$;
        """
        
        return self.apply_migration(migration_name, [create_index_query])
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """
        Retorna o histórico de migrações aplicadas
        
        Returns:
            Lista de migrações aplicadas
        """
        connection = None
        cursor = None
        
        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "SELECT migration_name, applied_at, status FROM schema_migrations ORDER BY applied_at DESC"
            )
            
            # Converter para lista de dicionários
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Erro ao obter histórico de migrações: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.db_manager.release_connection(connection)