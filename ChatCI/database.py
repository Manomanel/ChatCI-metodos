import sqlite3

class Database:
    def __init__(self, db_name="chatci.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        # Conecta ao banco e cria a tabela se não existir
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                tipo TEXT NOT NULL,
                bloqueado INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def get_connection(self):
        # Retorna uma conexão com o banco
        return sqlite3.connect(self.db_name)