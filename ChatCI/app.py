from flask import Flask, render_template, redirect, request

app = Flask(__name__)

@app.route("/")
def login():
   return render_template("login.html")

@app.route("/logar", methods=["POST"])
def logar():
   # Aqui poderia validar o login
   return redirect("/logado")

@app.route("/cadastro")
def cadastro():
   return render_template("cadastro.html")

@app.route("/finalizar_cadastro", methods=["POST"])
def finalizar_cadastro():
   # Aqui poderia salvar no banco de dados
   return redirect("/logado")

@app.route("/logado")
def logado():
   return render_template("logado.html")

if __name__ == "__main__":
   app.run(debug=True)
