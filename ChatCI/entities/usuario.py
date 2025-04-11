class Usuario:
   def __init__(self, nome, email, tipo):
      self.nome = nome
      self.email = email
      self.tipo = tipo  # Aluno, Professor, Administrador
      self.bloqueado = False

   def bloquear(self):
      self.bloqueado = True

   def desbloquear(self):
      self.bloqueado = False
