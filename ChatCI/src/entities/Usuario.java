public class Usuario {
    private String nome;
    private String email;
    private String tipo; // Aluno, Professor, Administrador
    private boolean bloqueado;

    public Usuario(String nome, String email, String tipo) {
        this.nome = nome;
        this.email = email;
        this.tipo = tipo;
        this.bloqueado = false;
    }

    public void bloquear() {
        this.bloqueado = true;
    }

    public void desbloquear() {
        this.bloqueado = false;
    }

    public String getNome() {
        return nome;
    }

    public String getEmail() {
        return email;
    }

    public String getTipo() {
        return tipo;
    }

    public boolean isBloqueado() {
        return bloqueado;
    }
}
