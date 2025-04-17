from flask import Flask, render_template, redirect, request, session, flash, jsonify
from controllers.user_management import UserManagement
from database.initializer import DatabaseInitializer
from database.manager import DatabaseManager
import logging
import os
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
from database.dao.factory.sql_dao_factory import SQLDAOFactory
from controllers.user_control import UserControl
from models.user import User

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
# Injetar a DAO no UserControl
factory = SQLDAOFactory()
user_dao = factory.create_user_dao()
user_control = UserControl(user_dao)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = os.getenv('APP_SECRET', 'chave_secreta_padrao')

user_mgmt = UserManagement()

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
    usuario = user_mgmt.validar_login(email, senha)
    if usuario:
        session['user_id'] = usuario.id
        session['username'] = usuario.name  
        session['nome'] = usuario.name      
        session['email'] = usuario.email
        session['matricula'] = usuario.matricula
        
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
    matricula = request.form.get("matricula")

    
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

    usuarios = user_mgmt.listar_usuarios()
    usuario_existente = next((u for u in usuarios if u.email == email), None)

    if usuario_existente:
        return render_template("cadastro.html", 
                              erro="Este email já está em uso",
                              nome=nome, 
                              tipo=tipo)

    user_id = user_mgmt.adicionar_usuario(nome, email, senha, matricula)
    
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
    profile = user_mgmt.profile_dao.get_by_user_id(user_id)
    
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

@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    user = User(
        id=None,  # o DAO atribui
        name=data["name"],
        email=data["email"],
        password=data["password"],
        matricula=data["matricula"]
    )
    user_control.add(user)
    return jsonify({"message": "Usuário adicionado com sucesso!"}), 201

@app.route("/users", methods=["GET"])
def list_users():
    users = user_control.list_all()
    return jsonify([user.__dict__ for user in users])

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user_control.delete(user_id)
    return jsonify({"message": "Usuário deletado com sucesso!"})
