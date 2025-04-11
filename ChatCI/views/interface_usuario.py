class InterfaceUsuario:
   def __init__(self, gerenciador):
      self.gerenciador = gerenciador

   def exibir_menu(self):
      while True:
         print("\n===== ChatCI - Menu Principal =====")
         print("1. Adicionar Usuário")
         print("2. Listar Usuários")
         print("3. Bloquear Usuário")
         print("4. Sair")
         opcao = input("Escolha uma opção: ")

         match opcao:
            case "1":
               self.adicionar_usuario()
            case "2":
               self.gerenciador.listar_usuarios()
            case "3":
               self.bloquear_usuario()
            case "4":
               print("Saindo...")
               break
            case _:
               print("Opção inválida. Tente novamente.")

   def adicionar_usuario(self):
      nome = input("Nome: ")
      email = input("Email: ")
      tipo = input("Tipo (Aluno, Professor, Administrador): ")
      self.gerenciador.adicionar_usuario(nome, email, tipo)

   def bloquear_usuario(self):
      email = input("Digite o email do usuário a ser bloqueado: ")
      self.gerenciador.bloquear_usuario(email)
