# manager.py
import psycopg2
from psycopg2 import pool
from config.settings import DB_CONFIG, MAX_CONNECTIONS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('database')

class DatabaseManager:
    """
    Classe Singleton para gerenciar a conexão com o banco de dados PostgreSQL.
    Implementa o padrão Singleton para garantir apenas uma instância da conexão.
    """
    _instance = None
    _connection_pool = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config=None):
        if self._initialized:
            return
        self.config = config if config is not None else DB_CONFIG
        self._create_connection_pool()
        self._initialized = True

    def _create_connection_pool(self, min_connections=1, max_connections=None):
        if max_connections is None:
            max_connections = MAX_CONNECTIONS
        try:
            self._connection_pool = pool.ThreadedConnectionPool(
                min_connections,
                max_connections,
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            logger.info("Pool de conexoes criado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar pool de conexoes: {e}")
            raise

    def get_connection(self):
        if self._connection_pool:
            return self._connection_pool.getconn()
        raise Exception("Pool de conexões nao inicializado.")

    def release_connection(self, connection):
        if self._connection_pool:
            self._connection_pool.putconn(connection)

    def close_all_connections(self):
        if self._connection_pool:
            self._connection_pool.closeall()
            logger.info("Todas as conexoes foram fechadas.")