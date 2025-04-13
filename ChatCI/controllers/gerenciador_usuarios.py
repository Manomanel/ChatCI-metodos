from entities.usuario import Usuario
import sqlite3
from database import Database

class GerenciadorUsuarios:
    def __init__(self):
        self.db = Database()

    def adicionar_usuario(self, nome, email, tipo, senha):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                (nome, email, senha, tipo)
            )
            conn.commit()
            print(f"Usuário {nome} adicionado com sucesso.")
        except sqlite3.IntegrityError:
            print("Erro: Usuário já cadastrado!")
        finally:
            conn.close()

    def bloquear_usuario(self, email):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET bloqueado = 1 WHERE email = ?", (email,))
        if cursor.rowcount > 0:
            print(f"Usuário com email {email} foi bloqueado.")
            conn.commit()
        else:
            print("Erro: Usuário não encontrado.")
        conn.close()

    def listar_usuarios(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, email, tipo, bloqueado FROM usuarios")
        usuarios = cursor.fetchall()
        if not usuarios:
            print("Nenhum usuário cadastrado.")
        else:
            for usuario in usuarios:
                nome, email, tipo, bloqueado = usuario
                status = "Bloqueado" if bloqueado else "Ativo"
                print(f"{nome} ({email}) - {tipo} [{status}]")
        conn.close()

    def validar_login(self, email, senha):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nome, email, tipo, senha, bloqueado FROM usuarios WHERE email = ?",
            (email,)
        )
        usuario = cursor.fetchone()
        conn.close()
        if usuario and usuario[3] == senha and not usuario[4]:
            return Usuario(usuario[0], usuario[1], usuario[2], usuario[3], usuario[4])
        return None