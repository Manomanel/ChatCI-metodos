import java.util.HashMap;
import java.util.Map;

public class GerenciadorUsuarios {
    private Map<String, Usuario> usuarios;

    public GerenciadorUsuarios() {
        this.usuarios = new HashMap<>();
    }

    public void adicionarUsuario(String nome, String email, String tipo) {
        if (usuarios.containsKey(email)) {
            System.out.println("Erro: Usuário já cadastrado!");
            return;
        }
        Usuario novoUsuario = new Usuario(nome, email, tipo);
        usuarios.put(email, novoUsuario);
        System.out.println("Usuário " + nome + " adicionado com sucesso.");
    }

    public void bloquearUsuario(String email) {
        Usuario usuario = usuarios.get(email);
        if (usuario != null) {
            usuario.bloquear();
            System.out.println("Usuário " + usuario.getNome() + " foi bloqueado.");
        } else {
            System.out.println("Erro: Usuário não encontrado.");
        }
    }

    public void listarUsuarios() {
        if (usuarios.isEmpty()) {
            System.out.println("Nenhum usuário cadastrado.");
            return;
        }
        for (Usuario usuario : usuarios.values()) {
            String status = usuario.isBloqueado() ? "Bloqueado" : "Ativo";
            System.out.println(usuario.getNome() + " (" + usuario.getEmail() + ") - " + usuario.getTipo() + " [" + status + "]");
        }
    }
}
