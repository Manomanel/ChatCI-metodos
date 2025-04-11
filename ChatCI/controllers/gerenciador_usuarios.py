from entities.usuario import Usuario

class GerenciadorUsuarios:
   def __init__(self):
      self.usuarios = {}

   def adicionar_usuario(self, nome, email, tipo):
      if email in self.usuarios:
         print("Erro: Usuário já cadastrado!")
         return

      novo_usuario = Usuario(nome, email, tipo)
      self.usuarios[email] = novo_usuario
      print(f"Usuário {nome} adicionado com sucesso.")

   def bloquear_usuario(self, email):
      usuario = self.usuarios.get(email)
      if usuario:
         usuario.bloquear()
         print(f"Usuário {usuario.nome} foi bloqueado.")
      else:
         print("Erro: Usuário não encontrado.")

   def listar_usuarios(self):
      if not self.usuarios:
         print("Nenhum usuário cadastrado.")
         return

      for usuario in self.usuarios.values():
         status = "Bloqueado" if usuario.bloqueado else "Ativo"
         print(f"{usuario.nome} ({usuario.email}) - {usuario.tipo} [{status}]")
