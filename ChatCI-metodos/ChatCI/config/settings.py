import os
from dotenv import load_dotenv

load_dotenv()

#voce deve criar um arquivo .env na raiz do projeto com as variaveis de ambiente do banco de dados nesse formato:
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=meubanco
# POSTGRES_USER=meuusuario
# POSTGRES_PASSWORD=minhasenha

# caso contrario ira criar um banco com essas credenciais padroes:
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', 5432),
    'database': os.getenv('POSTGRES_DB', 'chatci'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
}

# Configurações da aplicação
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
APP_ENV = os.getenv('APP_ENV', 'production')
APP_SECRET = os.getenv('APP_SECRET', 'chave_padrao_insegura')

# Outras configurações
TIMEOUT = int(os.getenv('TIMEOUT', '30'))
MAX_CONNECTIONS = int(os.getenv('MAX_CONNECTIONS', '10'))