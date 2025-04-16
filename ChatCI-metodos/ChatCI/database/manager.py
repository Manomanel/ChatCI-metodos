import psycopg2
from psycopg2 import pool
from typing import Dict, List, Any, Optional, Union, Tuple
from config.settings import DB_CONFIG, MAX_CONNECTIONS
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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

    def __init__(self, config: Dict[str, str] = None):
        if self._initialized:
            return
            
        # Se nenhuma config for fornecida, usa as variáveis de ambiente
        self.config = config if config is not None else DB_CONFIG
        self._create_connection_pool()
        self._initialized = True

    def _create_connection_pool(self, min_connections: int = 1, max_connections: int = None):
        """Cria um pool de conexões com o banco de dados."""
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
            logger.info(f"Pool de conexões criado com sucesso para {self.config['database']} em {self.config['host']}!")
        except Exception as e:
            logger.error(f"Erro ao criar pool de conexões: {e}")
            raise

    def get_connection(self):
        """Obtém uma conexão do pool."""
        if self._connection_pool:
            return self._connection_pool.getconn()
        raise Exception("Pool de conexões não inicializado!")

    def release_connection(self, connection):
        """Devolve uma conexão ao pool."""
        if self._connection_pool:
            self._connection_pool.putconn(connection)
        else:
            logger.warning("Tentativa de liberar conexão sem pool inicializado!")

    def close_all_connections(self):
        """Fecha todas as conexões no pool."""
        if self._connection_pool:
            self._connection_pool.closeall()
            logger.info("Todas as conexões foram fechadas.")
        else:
            logger.warning("Nenhum pool de conexões para fechar.")