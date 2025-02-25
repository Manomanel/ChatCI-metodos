public class Main {
    public static void main(String[] args) {
        GerenciadorUsuarios gerenciador = new GerenciadorUsuarios();
        InterfaceUsuario interfaceUsuario = new InterfaceUsuario(gerenciador);
        interfaceUsuario.exibirMenu();
    }
}
