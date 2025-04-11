from controllers.gerenciador_usuarios import GerenciadorUsuarios
from views.interface_usuario import InterfaceUsuario

def main():
   gerenciador = GerenciadorUsuarios()
   interface = InterfaceUsuario(gerenciador)
   interface.exibir_menu()

if __name__ == "__main__":
   main()
