from flask import Flask, render_template, redirect, request, session
from controllers.user_management import UserManagement
from database.initializer import DatabaseInitializer
from database.manager import DatabaseManager
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log')
    ]
)
logger = logging.getLogger('app')

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET', 'chave_secreta_padrao')

UserManagement = UserManagement()

def init_db():
    try:
        logger.info("Inicializando o banco de dados...")
        db_initializer = DatabaseInitializer()
        success = db_initializer.initialize_database()
        if success:
            logger.info("Banco de dados inicializado com sucesso!")
        else:
            logger.error("Falha ao inicializar o banco de dados!")
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/logar", methods=["POST"])
def logar():
    email = request.form.get("usuario")
    senha = request.form.get("senha")
    usuario = UserManagement.validar_login(email, senha)
    if usuario:
        session['user_id'] = usuario['id']
        session['username'] = usuario['username']
        session['nome'] = f"{usuario['first_name']} {usuario['last_name']}".strip()
        session['email'] = usuario['email']
        session['is_student'] = usuario['student']
        session['is_professor'] = usuario['professor']
        
        return redirect("/logado")
    return render_template("login.html", erro="Usuário ou senha incorretos")

@app.route("/cadastro", methods=["POST"])
def finalizar_cadastro():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    tipo = request.form.get("tipo")
    
    # Mapear os tipos do formulário para os valores esperados pelo backend
    tipo_mapeado = {
        "aluno": "Estudante",
        "professor": "Professor",
        "administrador": "Professor"  
    }.get(tipo, "Estudante")

    if not nome or not email or not senha or not tipo:
        return render_template("cadastro.html", 
                              erro="Todos os campos são obrigatórios",
                              nome=nome, 
                              email=email, 
                              tipo=tipo)

    usuario_existente = UserManagement.user_dao.get_user_by_email(email)
    if usuario_existente:
        return render_template("cadastro.html", 
                              erro="Este email já está em uso",
                              nome=nome, 
                              tipo=tipo)

    user_id = UserManagement.adicionar_usuario(nome, email, tipo_mapeado, senha)
    
    if user_id:
        return redirect("/")
    else:
        return render_template("cadastro.html", 
                              erro="Erro ao realizar cadastro. Tente novamente.",
                              nome=nome, 
                              email=email, 
                              tipo=tipo)

@app.route("/logado")
def logado():
    if 'user_id' not in session:
        return redirect("/")
    
    return render_template("logado.html", 
                          nome=session.get('nome'),
                          email=session.get('email'),
                          tipo="Aluno" if session.get('is_student') else "Professor")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

init_db()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)