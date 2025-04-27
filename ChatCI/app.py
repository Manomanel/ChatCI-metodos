from flask import Flask, render_template, redirect, request, session, flash, jsonify
from controllers.user_management import UserManagement
from database.initializer import DatabaseInitializer
from database.manager import DatabaseManager
from database.persistence.group_persistence import GroupPersistence
from bot.application import SACIApplication
import logging
import os
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_swagger_ui import get_swaggerui_blueprint
from flasgger import Swagger, swag_from

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

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "SACI Application API",
        "description": "API documentation for SACI application",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "basicAuth": {
            "type": "basic"
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

user_manager = UserManagement()
group_manager = GroupPersistence()

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
    """
    Login page
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Returns the login page
    """
    return render_template("login.html")

@app.route("/logar", methods=["POST"])
def logar():
    """
    User login
    ---
    tags:
      - Authentication
    parameters:
      - name: usuario
        in: formData
        type: string
        required: true
        description: User email
      - name: senha
        in: formData
        type: string
        required: true
        description: User password
    responses:
      302:
        description: Redirects to inicial page if login successful
      200:
        description: Returns login page with error if login failed
    """
    email = request.form.get("usuario")
    senha = request.form.get("senha")
    usuario = user_manager.validar_login(email, senha)
    if usuario:
        session['user_id'] = usuario['id']
        session['username'] = usuario['username']
        session['nome'] = f"{usuario['first_name']} {usuario['last_name']}".strip()
        session['email'] = usuario['email']
        session['is_student'] = usuario['student']
        session['is_professor'] = usuario['professor']
        session['is_superuser'] = usuario.get('is_superuser', False)
        
        return redirect("/inicial")
    return render_template("login.html", erro="Usuário ou senha incorretos")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    """
    Registration page and form processing
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Returns the registration page for GET, processes form for POST
      302:
        description: Redirects to login page if registration successful
    """
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        tipo = request.form.get("tipo")
        
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

        usuario_existente = user_manager.user_persistence.get_user_by_email(email)
        if usuario_existente:
            return render_template("cadastro.html",
                                  erro="Este email já está em uso",
                                  nome=nome,
                                  tipo=tipo)

        user_id = user_manager.adicionar_usuario(nome, email, tipo_mapeado, senha)
        
        if user_id:
            flash("Cadastro realizado com sucesso! Você pode fazer login agora.", "success")
            return redirect("/")
        else:
            return render_template("cadastro.html",
                                  erro="Erro ao realizar cadastro. Tente novamente.",
                                  nome=nome,
                                  email=email,
                                  tipo=tipo)
    else:
        return render_template("cadastro.html")

@app.route("/inicial")
def inicial():
    """
    Main dashboard page
    ---
    tags:
      - Dashboard
    responses:
      200:
        description: Returns the main dashboard
      302:
        description: Redirects to login if not authenticated
    """
    if 'user_id' not in session:
        return redirect("/")

    user_id = session.get('user_id')
    user_groups = group_manager.get_user_groups(user_id)
    
    return render_template("inicial.html", user_groups=user_groups)

@app.route("/perfil")
def profile():
    """
    User profile page
    ---
    tags:
      - Profile
    responses:
      200:
        description: Returns the user profile page
      302:
        description: Redirects to login if not authenticated
    """
    if 'user_id' not in session:
        return redirect("/")
    
    user_id = session.get('user_id')
    profile = user_manager.profile_dao.get_by_user_id(user_id)
    
    if not profile:
        user_manager.profile_dao.create(user_id, bio="", profile_picture=None)
        profile = user_manager.profile_dao.get_by_user_id(user_id)
    
    return render_template("perfil.html", 
                          nome=session.get('nome'),
                          email=session.get('email'),
                          bio=profile['bio'],
                          profile_picture=profile.get('profile_picture'))

@app.route("/logout")
def logout():
    """
    User logout
    ---
    tags:
      - Authentication
    responses:
      302:
        description: Redirects to login page
    """
    session.clear()
    return redirect("/")

@app.route("/admin")
def admin_dashboard():
    """
    Admin dashboard
    ---
    tags:
      - Admin
    responses:
      200:
        description: Returns the admin dashboard
      302:
        description: Redirects to login if not authenticated or not admin
    """
    if 'user_id' not in session:
        return redirect("/")
    
    if not session.get('is_professor') and not session.get('is_superuser'):
        flash("Acesso negado. Área restrita para administradores.", "error")
        return redirect("/inicial")
    
    return render_template("admin/dashboard.html")

@app.route("/admin/scrape-saci", methods=["POST"])
def admin_scrape_saci():
    """
    Execute SACI scraping integration
    ---
    tags:
      - Admin
    responses:
      200:
        description: Returns integration results
        schema:
          type: object
          properties:
            success:
              type: boolean
            turmas_found:
              type: integer
            groups_created:
              type: integer
            groups_existing:
              type: integer
            errors:
              type: array
              items:
                type: string
      401:
        description: Unauthorized
      403:
        description: Forbidden
      500:
        description: Server error
    """
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Não autorizado"}), 401
    
    if not session.get('is_professor') and not session.get('is_superuser'):
        return jsonify({"success": False, "error": "Acesso negado"}), 403
    
    try:
        saci_app = SACIApplication()
        result = saci_app.run_integration()
        
        return jsonify({
            "success": True,
            "turmas_found": result['turmas_found'],
            "groups_created": result['groups_created'],
            "groups_existing": result['groups_existing'],
            "errors": result['errors']
        })
    except Exception as e:
        logger.error(f"Erro na integração SACI: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/grupos")
def grupos():
    """
    Groups list page
    ---
    tags:
      - Groups
    responses:
      200:
        description: Returns the groups list page
      302:
        description: Redirects to login if not authenticated
    """
    if 'user_id' not in session:
        return redirect("/")

    all_groups = group_manager.get_all_groups()
    user_id = session.get('user_id')
    user_groups = group_manager.get_user_groups(user_id)
    user_group_ids = [group['id'] for group in user_groups]
    
    return render_template("grupos.html", 
                         groups=all_groups, 
                         user_groups=user_group_ids)

@app.route("/grupo/<int:grupo_id>")
def grupo_chat(grupo_id):
    """
    Group chat page
    ---
    tags:
      - Groups
    parameters:
      - name: grupo_id
        in: path
        type: integer
        required: true
        description: Group ID
    responses:
      200:
        description: Returns the group chat page
      302:
        description: Redirects to groups list if not a member
    """
    if 'user_id' not in session:
        return redirect("/")

    user_id = session.get('user_id')
    if not group_manager.is_member(grupo_id, user_id):
        flash("Você precisa entrar no grupo primeiro.", "error")
        return redirect("/grupos")
    
    group = group_manager.get_group_by_id(grupo_id)
    return render_template("chat.html", grupo_id=grupo_id, group=group)

@app.route("/entrar-grupo/<int:grupo_id>", methods=["POST"])
def entrar_grupo(grupo_id):
    """
    Join a group
    ---
    tags:
      - Groups
    parameters:
      - name: grupo_id
        in: path
        type: integer
        required: true
        description: Group ID
    responses:
      302:
        description: Redirects to groups list after joining
    """
    if 'user_id' not in session:
        return redirect("/")
    
    user_id = session.get('user_id')
    if group_manager.add_member(grupo_id, user_id):
        flash("Você entrou no grupo com sucesso!", "success")
    else:
        flash("Erro ao entrar no grupo.", "error")
    
    return redirect("/grupos")

# @app.errorhandler(404)
# def page_not_found(e):
#     """
#     404 error handler
#     ---
#     tags:
#       - Error
#     responses:
#       404:
#         description: Page not found
#     """
#     return render_template('404.html'), 404

init_db()

if __name__ == "__main__":
    try:
        db_manager = DatabaseManager()
        app.run(debug=True, host='0.0.0.0', port=5001)
    except Exception as e:
        logger.error(f"Erro ao iniciar o aplicativo: {e}")
    finally:
        try:
            db_manager = DatabaseManager()
            db_manager.close_all_connections()
        except:
            pass