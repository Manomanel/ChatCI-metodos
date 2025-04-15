from flask import Flask, render_template, redirect, request, session, flash
from controllers.user_management import UserManagement
from database.initializer import DatabaseInitializer
from database.manager import DatabaseManager
import logging
import os
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

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
app.wsgi_app = ProxyFix(app.wsgi_app)
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

@app.route("/inicial")
def inicial():
    return render_template("inicial.html")

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
        
        return redirect("/inicial")
    return render_template("login.html", erro="Usuário ou senha incorretos")

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/finalizar_cadastro", methods=["POST"])
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
        flash("Cadastro realizado com sucesso! Você pode fazer login agora.", "success")
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

@app.route("/perfil")
def profile():
    if 'user_id' not in session:
        return redirect("/")
    
    user_id = session.get('user_id')
    profile = UserManagement.profile_dao.get_by_user_id(user_id)
    
    if not profile:
        return redirect("/logado")
    
    return render_template("perfil.html", 
                          nome=session.get('nome'),
                          email=session.get('email'),
                          bio=profile['bio'],
                          profile_picture=profile['profile_picture'])

init_db()

if __name__ == "__main__":
    try:
        db_manager = DatabaseManager()
        app.run(debug=True, host='0.0.0.0', port=5001)
    except Exception as e:
        logger.error(f"Erro ao iniciar o aplicativo: {e}")
    finally:
        # Garantir que todas as conexões sejam fechadas quando o aplicativo for encerrado
        try:
            db_manager = DatabaseManager()
            db_manager.close_all_connections()
        except:
            pass