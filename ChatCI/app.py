from flask import Flask, render_template, redirect, request
from controllers.gerenciador_usuarios import GerenciadorUsuarios

app = Flask(__name__)
gerenciador = GerenciadorUsuarios()

#rotas da tela de login
@app.route("/")
def login():
    return render_template("login.html")

@app.route("/logar", methods=["POST"])
def logar():
    email = request.form.get("usuario")
    senha = request.form.get("senha")
    usuario = gerenciador.validar_login(email, senha)
    if usuario:
        return redirect("/inicial")
    return render_template("login.html", erro="Usuário ou senha incorretos")

#rotas da tela de cadastro
@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/finalizar_cadastro", methods=["POST"])
def finalizar_cadastro():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    tipo = request.form.get("tipo").capitalize()
    gerenciador.adicionar_usuario(nome, email, tipo, senha)
    return redirect("/inicial")

#rotas da tela inicial
@app.route("/inicial")
def inicial():
    return render_template("inicial.html")

#rotas da tela de perfil
@app.route("/perfil")
def perfil():
   return render_template("perfil.html")

if __name__ == "__main__":
    app.run(debug=True)