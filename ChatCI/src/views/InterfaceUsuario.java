import java.util.Scanner;

public class InterfaceUsuario {
    private GerenciadorUsuarios gerenciador;

    public InterfaceUsuario(GerenciadorUsuarios gerenciador) {
        this.gerenciador = gerenciador;
    }

    public void exibirMenu() {
        Scanner scanner = new Scanner(System.in);
        while (true) {
            System.out.println("\n===== ChatCI - Menu Principal =====");
            System.out.println("1. Adicionar Usuário");
            System.out.println("2. Listar Usuários");
            System.out.println("3. Bloquear Usuário");
            System.out.println("4. Sair");
            System.out.print("Escolha uma opção: ");

            String opcao = scanner.nextLine();

            switch (opcao) {
                case "1":
                    adicionarUsuario(scanner);
                    break;
                case "2":
                    gerenciador.listarUsuarios();
                    break;
                case "3":
                    bloquearUsuario(scanner);
                    break;
                case "4":
                    System.out.println("Saindo...");
                    scanner.close();
                    return;
                default:
                    System.out.println("Opção inválida. Tente novamente.");
            }
        }
    }

    private void adicionarUsuario(Scanner scanner) {
        System.out.print("Nome: ");
        String nome = scanner.nextLine();
        System.out.print("Email: ");
        String email = scanner.nextLine();
        System.out.print("Tipo (Aluno, Professor, Administrador): ");
        String tipo = scanner.nextLine();
        gerenciador.adicionarUsuario(nome, email, tipo);
    }

    private void bloquearUsuario(Scanner scanner) {
        System.out.print("Digite o email do usuário a ser bloqueado: ");
        String email = scanner.nextLine();
        gerenciador.bloquearUsuario(email);
    }
}
