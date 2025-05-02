from flask import Flask, jsonify, request, session
from controllers.user_management import UserManagement
from database.initializer import DatabaseInitializer
from database.manager import DatabaseManager
from database.persistence.group_persistence import GroupPersistence
from database.persistence.message_persistence import MessagePersistence
from database.persistence.event_persistence import EventPersistence
import logging
import os
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
from views.chatCIFacade import ChatCIFacade
from flasgger import Swagger
from flask_cors import CORS
from functools import wraps
from mediator.mediator import Mediator
from components.components import SACIBotComponent, GroupManagerComponent, MessageManagerComponent
from datetime import datetime

facade = ChatCIFacade()
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

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True,
        "expose_headers": ["Set-Cookie"]
    }
})

# Middleware para tratar erros de SSL/TLS
@app.before_request
def before_request():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    # Verifica se a requisição está tentando usar HTTPS em um servidor HTTP
    if request.is_secure and not app.config.get('PREFERRED_URL_SCHEME') == 'https':
        return jsonify({
            "success": False,
            "error": "Esta API não suporta HTTPS"
        }), 400

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
        "title": "C API",
        "description": "API documentation for SACI application",
        "version": "1.0.0"
    },
    "basePath": "/api",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "bearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
        },
        "sessionAuth": {
            "type": "apiKey",
            "name": "Cookie",
            "in": "header",
            "description": "Cookie-based session authentication"
        }
    },
    "security": [
        {
            "bearerAuth": []
        },
        {
            "sessionAuth": []
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Decorador para rotas que requerem autenticação
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                "success": False,
                "error": "Autenticação necessária"
            }), 401
        return f(*args, **kwargs)
    return decorated_function

# Decorador para rotas que requerem permissão de admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                "success": False,
                "error": "Autenticação necessária"
            }), 401
        
        if not session.get('is_professor') and not session.get('is_superuser'):
            return jsonify({
                "success": False,
                "error": "Permissão de administrador necessária"
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

user_manager = UserManagement()
# instancia de cada dao
group_manager = GroupPersistence()
message_manager = MessagePersistence()
event_manager = EventPersistence()

# MEDIATOR PARA MENSAGENS E GRUPOS
mediator = Mediator()
mediator.set_daos(group_manager, message_manager)

saci_component = SACIBotComponent()
group_component = GroupManagerComponent()
message_component = MessageManagerComponent()

mediator.register_component('bot', saci_component)
mediator.register_component('group_manager', group_component)
mediator.register_component('message_manager', message_component)

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
        
# ENDPOINTS ----------------------------------------------------

@app.route("/api/test-auth", methods=["GET"])
@login_required
def test_auth():
    """
    Test authentication status
    ---
    tags:
      - Authentication
    security:
      - bearerAuth: []
      - sessionAuth: []
    responses:
      200:
        description: Authenticated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            user:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
                is_admin:
                  type: boolean
      401:
        description: Not authenticated
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    return jsonify({
        "success": True,
        "message": "Você está autenticado",
        "user": {
            "id": session.get('user_id'),
            "username": session.get('username'),
            "is_admin": session.get('is_professor') or session.get('is_superuser')
        }
    })

@app.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    """
    User login
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              description: User email
            senha:
              type: string
              description: User password
          required:
            - email
            - senha
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            user:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
                nome:
                  type: string
                email:
                  type: string
                is_student:
                  type: boolean
                is_professor:
                  type: boolean
                is_superuser:
                  type: boolean
      401:
        description: Login failed
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    if request.method == "OPTIONS":
        return jsonify({}), 200
        
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type deve ser application/json"
            }), 400
            
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Dados não recebidos"
            }), 400
            
        email = data.get("email")
        senha = data.get("senha")
        
        if not email or not senha:
            return jsonify({
                "success": False,
                "error": "Email e senha são obrigatórios"
            }), 400
        
        usuario = facade.login(email, senha)
        
        if usuario:
            session['user_id'] = usuario['id']
            session['username'] = usuario['username']
            session['nome'] = f"{usuario['first_name']} {usuario['last_name']}".strip()
            session['email'] = usuario['email']
            session['is_student'] = usuario['student']
            session['is_professor'] = usuario['professor']
            session['is_superuser'] = usuario.get('is_superuser', False)
            
            # Marca a sessão como permanente
            session.permanent = True
            
            return jsonify({
                "success": True,
                "message": "Login realizado com sucesso",
                "user": {
                    "id": usuario['id'],
                    "username": usuario['username'],
                    "nome": session['nome'],
                    "email": usuario['email'],
                    "is_student": usuario['student'],
                    "is_professor": usuario['professor'],
                    "is_superuser": usuario.get('is_superuser', False)
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": "Usuário ou senha incorretos"
            }), 401
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/cadastro", methods=["POST", "OPTIONS"])
def cadastro():
    """
    User registration
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            primeiro_nome:
              type: string
            ultimo_nome:
              type: string
            email:
              type: string
            senha:
              type: string
            tipo:
              type: string
              enum: [aluno, professor, admin, superuser]
          required:
            - username
            - primeiro_nome
            - ultimo_nome
            - email
            - senha
            - tipo
    responses:
      200:
        description: Registration successful
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            user_id:
              type: integer
      400:
        description: Registration failed
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    if request.method == "OPTIONS":
        return jsonify({}), 200
        
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type deve ser application/json"
            }), 400
            
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Dados não recebidos"
            }), 400
            
        nome = data.get("username")
        first_name = data.get("primeiro_nome")
        last_name = data.get("ultimo_nome")
        email = data.get("email")
        senha = data.get("senha")
        tipo = data.get("tipo")
        
        tipo_mapeado = {
            "aluno": "Estudante",
            "professor": "Professor",
            "admin": "Professor",
            "superuser": "Professor"
        }.get(tipo, "Estudante")

        is_superuser = tipo in ["admin", "superuser"]

        if not all([nome, email, senha, tipo, first_name, last_name]):
            return jsonify({
                "success": False,
                "error": "Todos os campos são obrigatórios"
            }), 400

        # Chama o método existente, mas passa informações adicionais
        user_id, erro = facade.cadastrar_usuario(
                nome, 
                first_name, 
                last_name, 
                email, 
                tipo_mapeado, 
                senha, 
                is_superuser 
            )
        
        if erro:
            return jsonify({
                "success": False,
                "error": erro
            }), 400
        
        if user_id:
            return jsonify({
                "success": True,
                "message": "Cadastro realizado com sucesso!",
                "user_id": user_id
            })
        else:
            return jsonify({
                "success": False,
                "error": "Erro ao realizar cadastro"
            }), 400
    except Exception as e:
        logger.error(f"Erro no cadastro: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/perfil", methods=["GET"])
@login_required
def perfil():
    """
    Get user profile
    ---
    tags:
      - Profile
    security:
      - bearerAuth: []
      - sessionAuth: []
    responses:
      200:
        description: Profile retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            profile:
              type: object
              properties:
                nome:
                  type: string
                email:
                  type: string
                bio:
                  type: string
                profile_picture:
                  type: string
      401:
        description: Not authorized
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    try:
        user_id = session.get('user_id')
        profile = facade.buscar_perfil(user_id)
        
        if not profile:
            user_manager.profile_dao.create(user_id, bio="", profile_picture=None)
            profile = user_manager.profile_dao.get_by_user_id(user_id)
        
        return jsonify({
            "success": True,
            "profile": {
                "nome": session.get('nome'),
                "email": session.get('email'),
                "bio": profile.get('bio', ''),
                "profile_picture": profile.get('profile_picture')
            }
        })
    except Exception as e:
        logger.error(f"Erro ao buscar perfil: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

@app.route("/api/grupos", methods=["GET"])
def grupos():
    """
    Get all groups and user's groups
    ---
    tags:
      - Groups
    responses:
      200:
        description: Groups retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            all_groups:
              type: array
              items:
                type: object
            user_groups:
              type: array
              items:
                type: integer
      401:
        description: Not authorized
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Não autorizado"}), 401
    
    try:
        all_groups = group_manager.get_all_groups()
        user_id = session.get('user_id')
        user_groups = group_manager.get_user_groups(user_id)
        user_group_ids = [group['id'] for group in user_groups]
        
        return jsonify({
            "success": True,
            "all_groups": all_groups,
            "user_groups": user_group_ids
        })
    except Exception as e:
        logger.error(f"Erro ao buscar grupos: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

@app.route("/api/grupos/<int:grupo_id>", methods=["GET"])
def grupo_detalhes(grupo_id):
    """
    Get group details
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
        description: Group details retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            group:
              type: object
      401:
        description: Not authorized
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      403:
        description: Not a member of the group
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Não autorizado"}), 401
    
    try:
        user_id = session.get('user_id')
        
        if not group_manager.is_member(grupo_id, user_id):
            return jsonify({
                "success": False,
                "error": "Você não é membro deste grupo"
            }), 403
        
        group = group_manager.get_group_by_id(grupo_id)
        
        if not group:
            return jsonify({
                "success": False,
                "error": "Grupo não encontrado"
            }), 404
        
        return jsonify({
            "success": True,
            "group": group
        })
    except Exception as e:
        logger.error(f"Erro ao buscar detalhes do grupo: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

@app.route("/api/grupos/<int:grupo_id>/entrar", methods=["POST"])
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
      200:
        description: Successfully joined the group
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
      400:
        description: Failed to join the group
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      401:
        description: Not authorized
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Não autorizado"}), 401
    
    try:
        user_id = session.get('user_id')
        
        if group_manager.add_member(grupo_id, user_id):
            return jsonify({
                "success": True,
                "message": "Você entrou no grupo com sucesso!"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Erro ao entrar no grupo."
            }), 400
    except Exception as e:
        logger.error(f"Erro ao entrar no grupo: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

@app.route("/api/grupos/<int:grupo_id>/mensagens", methods=["POST"])
def enviar_mensagem(grupo_id):
    """
    Send a message to a group
    ---
    tags:
      - Messages
    parameters:
      - name: grupo_id
        in: path
        type: integer
        required: true
        description: Group ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
              description: Message text
          required:
            - text
    responses:
      200:
        description: Message sent successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message_id:
              type: integer
      400:
        description: Bad request
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      401:
        description: Not authorized
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      403:
        description: Not a member of the group
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Não autorizado"}), 401
    
    try:
        user_id = session.get('user_id')
        
        if not group_manager.is_member(grupo_id, user_id):
            return jsonify({
                "success": False,
                "error": "Você não é membro deste grupo"
            }), 403
        
        data = request.get_json()
        text = data.get('text')
        
        if not text:
            return jsonify({
                "success": False,
                "error": "Texto da mensagem é obrigatório"
            }), 400

        message_id = mediator.notify("SEND_MESSAGE", {
            "group_id": grupo_id,
            "user_id": user_id,
            "text": text
        })
        
        if message_id:
            return jsonify({
                "success": True,
                "message_id": message_id
            })
        else:
            return jsonify({
                "success": False,
                "error": "Erro ao enviar mensagem"
            }), 500
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500
        
@app.route("/api/usuarios/grupos", methods=["GET"])
def get_user_groups():
    """
    Get groups that the current user is a member of
    ---
    tags:
      - Groups
    responses:
      200:
        description: User groups retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            groups:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  description:
                    type: string
                  created_at:
                    type: string
                    format: date-time
      401:
        description: Not authorized
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Não autorizado"}), 401
    
    try:
        user_id = session.get('user_id')

        groups = group_manager.get_user_groups(user_id)
        
        return jsonify({
            "success": True,
            "groups": groups
        })
    except Exception as e:
        logger.error(f"Erro ao buscar grupos do usuário: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

@app.route("/api/grupos/<int:grupo_id>/mensagens", methods=["GET"])
def get_mensagens(grupo_id):
    """
    Get messages from a group
    ---
    tags:
      - Messages
    parameters:
      - name: grupo_id
        in: path
        type: integer
        required: true
        description: Group ID
      - name: limit
        in: query
        type: integer
        required: false
        description: Number of messages to return (default 50)
      - name: offset
        in: query
        type: integer
        required: false
        description: Number of messages to skip (default 0)
    responses:
      200:
        description: Messages retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            messages:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  user_id:
                    type: integer
                  username:
                    type: string
                  text:
                    type: string
                  created_at:
                    type: string
                    format: date-time
      401:
        description: Not authorized
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      403:
        description: Not a member of the group
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Não autorizado"}), 401
    
    try:
        user_id = session.get('user_id')
        
        if not group_manager.is_member(grupo_id, user_id):
            return jsonify({
                "success": False,
                "error": "Você não é membro deste grupo"
            }), 403
        
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        messages = message_manager.get_group_messages(grupo_id, limit, offset)
        
        return jsonify({
            "success": True,
            "messages": messages
        })
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500
        
@app.route("/api/grupos/<int:grupo_id>/membros/<int:user_id>/banir", methods=["POST"])
@admin_required
def banir_membro(grupo_id, user_id):
    """
    Ban a user from a group
    ---
    tags:
      - Groups
    security:
      - bearerAuth: []
      - sessionAuth: []
    parameters:
      - name: grupo_id
        in: path
        type: integer
        required: true
        description: Group ID
      - name: user_id
        in: path
        type: integer
        required: true
        description: User ID to ban
    responses:
      200:
        description: User banned successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
      400:
        description: Failed to ban user
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      401:
        description: Not authorized
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      403:
        description: Not allowed
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      404:
        description: Group or user not found
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    try:
        group = group_manager.get_group_by_id(grupo_id)
        if not group:
            return jsonify({
                "success": False,
                "error": "Grupo não encontrado"
            }), 404

        from controllers.user_management import UserManagement
        user_manager = UserManagement()
        user = user_manager.get_user_by_id(user_id)
        if not user:
            return jsonify({
                "success": False,
                "error": "Usuário não encontrado"
            }), 404

        if group_manager.is_banned(grupo_id, user_id):
            return jsonify({
                "success": False,
                "error": "Usuário já está banido deste grupo"
            }), 400

        if group_manager.ban_user(grupo_id, user_id):
            return jsonify({
                "success": True,
                "message": "Usuário banido com sucesso"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Erro ao banir usuário"
            }), 500
            
    except Exception as e:
        logger.error(f"Erro ao banir usuário: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

@app.route("/api/grupos/<int:grupo_id>/membros/<int:user_id>/desbanir", methods=["POST"])
@admin_required
def desbanir_membro(grupo_id, user_id):
    """
    Unban a user from a group
    ---
    tags:
      - Groups
    security:
      - bearerAuth: []
      - sessionAuth: []
    parameters:
      - name: grupo_id
        in: path
        type: integer
        required: true
        description: Group ID
      - name: user_id
        in: path
        type: integer
        required: true
        description: User ID to unban
    responses:
      200:
        description: User unbanned successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
      400:
        description: Failed to unban user
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      401:
        description: Not authorized
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      403:
        description: Not allowed
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      404:
        description: Group or user not found
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    try:
        group = group_manager.get_group_by_id(grupo_id)
        if not group:
            return jsonify({
                "success": False,
                "error": "Grupo não encontrado"
            }), 404

        from controllers.user_management import UserManagement
        user_manager = UserManagement()
        user = user_manager.get_user_by_id(user_id)
        if not user:
            return jsonify({
                "success": False,
                "error": "Usuário não encontrado"
            }), 404

        if not group_manager.is_banned(grupo_id, user_id):
            return jsonify({
                "success": False,
                "error": "Usuário não está banido deste grupo"
            }), 400

        if group_manager.unban_user(grupo_id, user_id):
            return jsonify({
                "success": True,
                "message": "Usuário desbanido com sucesso"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Erro ao desbanir usuário"
            }), 500
            
    except Exception as e:
        logger.error(f"Erro ao desbanir usuário: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

@app.route("/api/grupos/<int:grupo_id>/membros", methods=["GET"])
@login_required
def listar_membros_grupo(grupo_id):
    """
    List all members of a group
    ---
    tags:
      - Groups
    security:
      - bearerAuth: []
      - sessionAuth: []
    parameters:
      - name: grupo_id
        in: path
        type: integer
        required: true
        description: Group ID
    responses:
      200:
        description: Group members retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            members:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  username:
                    type: string
                  nome:
                    type: string
                  email:
                    type: string
      401:
        description: Not authorized
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      403:
        description: Not a member of the group
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      404:
        description: Group not found
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    try:
        user_id = session.get('user_id')

        group = group_manager.get_group_by_id(grupo_id)
        if not group:
            return jsonify({
                "success": False,
                "error": "Grupo não encontrado"
            }), 404

        if not group_manager.is_member(grupo_id, user_id) and not session.get('is_professor') and not session.get('is_superuser'):
            return jsonify({
                "success": False,
                "error": "Você não é membro deste grupo"
            }), 403

        members = group_manager.get_group_members(grupo_id)

        formatted_members = []
        for member in members:
            formatted_members.append({
                "id": member['id'],
                "username": member['username'],
                "nome": f"{member['first_name']} {member['last_name']}".strip(),
                "email": member['email']
            })
        
        return jsonify({
            "success": True,
            "members": formatted_members
        })
            
    except Exception as e:
        logger.error(f"Erro ao listar membros do grupo: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

@app.route("/api/grupos/<int:grupo_id>/membros/banidos", methods=["GET"])
@admin_required
def listar_membros_banidos(grupo_id):
    """
    List all banned members of a group
    ---
    tags:
      - Groups
    security:
      - bearerAuth: []
      - sessionAuth: []
    parameters:
      - name: grupo_id
        in: path
        type: integer
        required: true
        description: Group ID
    responses:
      200:
        description: Banned members retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            banned_members:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  username:
                    type: string
                  nome:
                    type: string
                  email:
                    type: string
      401:
        description: Not authorized
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      403:
        description: Not allowed
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      404:
        description: Group not found
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    try:
        group = group_manager.get_group_by_id(grupo_id)
        if not group:
            return jsonify({
                "success": False,
                "error": "Grupo não encontrado"
            }), 404

        banned_members = group_manager.get_banned_members(grupo_id)

        formatted_banned_members = []
        for member in banned_members:
            formatted_banned_members.append({
                "id": member['id'],
                "username": member['username'],
                "nome": f"{member['first_name']} {member['last_name']}".strip(),
                "email": member['email']
            })
        
        return jsonify({
            "success": True,
            "banned_members": formatted_banned_members
        })
            
    except Exception as e:
        logger.error(f"Erro ao listar membros banidos do grupo: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

@app.route("/api/logout", methods=["POST"])
def logout():
    """
    User logout
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Logout successful
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
    """
    try:
        session.clear()
        return jsonify({
            "success": True,
            "message": "Logout realizado com sucesso"
        })
    except Exception as e:
        logger.error(f"Erro no logout: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

@app.route("/api/admin/scrape-saci", methods=["POST"])
@admin_required
def admin_scrape_saci():
    """
    Execute SACI scraping integration
    ---
    tags:
      - Admin
    security:
      - bearerAuth: []
      - sessionAuth: []
    responses:
      200:
        description: Integration results
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
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      403:
        description: Forbidden
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    try:
        # Usar o Mediator para executar a integração
        result = mediator.notify("RUN_INTEGRATION")
        
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

@app.route("/api/eventos", methods=["GET"])
def get_eventos():
    """
    Get all events
    ---
    tags:
      - Events
    responses:
      200:
        description: Events retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            events:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  title:
                    type: string
                  description:
                    type: string
                  link:
                    type: string
                  event_date:
                    type: string
                    format: date
                  created_at:
                    type: string
                    format: date-time
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    try:
        
        events = event_manager.get_all_events()
        
        return jsonify({
            "success": True,
            "events": events
        })
    except Exception as e:
        logger.error(f"Erro ao buscar eventos: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

@app.route("/api/eventos/<int:evento_id>", methods=["GET"])
def get_evento(evento_id):
    """
    Get event details
    ---
    tags:
      - Events
    parameters:
      - name: evento_id
        in: path
        type: integer
        required: true
        description: Event ID
    responses:
      200:
        description: Event details retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            event:
              type: object
              properties:
                id:
                  type: integer
                title:
                  type: string
                description:
                  type: string
                link:
                  type: string
                event_date:
                  type: string
                  format: date
                created_at:
                  type: string
                  format: date-time
      404:
        description: Event not found
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    try:
        event = event_manager.get_event_by_id(evento_id)
        
        if not event:
            return jsonify({
                "success": False,
                "error": "Evento não encontrado"
            }), 404
        
        return jsonify({
            "success": True,
            "event": event
        })
    except Exception as e:
        logger.error(f"Erro ao buscar evento: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

#CRIA O EVENTO
@app.route("/api/eventos/criar", methods=["POST"])
@admin_required
def criar_evento():
    """
    Create a new event
    ---
    tags:
      - Events
    security:
      - bearerAuth: []
      - sessionAuth: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            titulo:
              type: string
              description: Título do evento
            descricao:
              type: string
              description: Descrição completa do evento
            data:
              type: string
              format: date
              description: Data do evento (YYYY-MM-DD)
            hora:
              type: string
              format: time
              description: Hora do evento (HH:MM)
            local:
              type: string
              description: Local do evento
          required:
            - titulo
            - descricao
            - data
            - hora
            - local
    responses:
      200:
        description: Event created successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            event_id:
              type: integer
      400:
        description: Invalid request
      401:
        description: Unauthorized
      403:
        description: Forbidden
      500:
        description: Server error
    """
    if request.method == "OPTIONS":
        return jsonify({}), 200
        
    try:
        if not request.is_json:
            return jsonify({"success": False, "error": "Content-Type deve ser application/json"}), 400
            
        data = request.get_json()
        
        required_fields = ['titulo', 'descricao', 'data', 'hora', 'local']
        if not all(field in data for field in required_fields):
            return jsonify({"success": False, "error": "Todos os campos são obrigatórios"}), 400

        try:
            event_datetime = datetime.strptime(f"{data['data']} {data['hora']}", "%Y-%m-%d %H:%M")
        except ValueError:
            return jsonify({"success": False, "error": "Formato de data/hora inválido"}), 400
        
        event_id = event_manager.create_event(
            title=data['titulo'],
            description=data['descricao'],
            local=data['local'],
            event_date=event_datetime
        )
        
        return jsonify({
            "success": True,
            "message": "Evento criado com sucesso",
            "event_id": event_id
        })
        
    except Exception as e:
        logger.error(f"Erro ao criar evento: {str(e)}")
        return jsonify({"success": False, "error": "Erro interno do servidor"}), 500

#ATUALIZA O EVENTO POR ID
@app.route("/api/eventos/<int:evento_id>", methods=["PUT"])
@admin_required
def atualizar_evento(evento_id):
    """
    Update an event
    ---
    tags:
      - Events
    security:
      - bearerAuth: []
      - sessionAuth: []
    parameters:
      - name: evento_id
        in: path
        type: integer
        required: true
        description: Event ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              description: Event title
            description:
              type: string
              description: Event description
            link:
              type: string
              description: Event related link
            event_date:
              type: string
              format: date
              description: Event date (YYYY-MM-DD or ISO format)
    responses:
      200:
        description: Event updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
      400:
        description: Invalid request
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      403:
        description: Forbidden
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      404:
        description: Event not found
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    if request.method == "OPTIONS":
        return jsonify({}), 200
        
    try:
        event = event_manager.get_event_by_id(evento_id)
        if not event:
            return jsonify({
                "success": False,
                "error": "Evento não encontrado"
            }), 404

        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type deve ser application/json"
            }), 400
            
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Dados não recebidos"
            }), 400
            
        title = data.get("title")
        description = data.get("description")
        link = data.get("link")
        event_date_str = data.get("event_date")
        
        event_date = None
        if event_date_str:
            try:
                if 'T' in event_date_str:
                    event_date_str = event_date_str.split('T')[0]

                event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "Formato de data inválido. Use YYYY-MM-DD ou formato ISO"
                }), 400

        success = event_manager.update_event(
            evento_id,
            title=title,
            description=description,
            link=link,
            event_date=event_date
        )
        
        if success:
            return jsonify({
                "success": True,
                "message": "Evento atualizado com sucesso"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Erro ao atualizar evento"
            }), 500
    except Exception as e:
        logger.error(f"Erro ao atualizar evento: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

@app.route("/api/eventos/<int:evento_id>", methods=["DELETE"])
@admin_required
def deletar_evento(evento_id):
    """
    Delete an event
    ---
    tags:
      - Events
    security:
      - bearerAuth: []
      - sessionAuth: []
    parameters:
      - name: evento_id
        in: path
        type: integer
        required: true
        description: Event ID
    responses:
      200:
        description: Event deleted successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      403:
        description: Forbidden
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      404:
        description: Event not found
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    try:
        # Verifica se o evento existe
        event = event_manager.get_event_by_id(evento_id)
        if not event:
            return jsonify({
                "success": False,
                "error": "Evento não encontrado"
            }), 404
            
        # Remove o evento
        success = event_manager.delete_event(evento_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Evento removido com sucesso"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Erro ao remover evento"
            }), 500
    except Exception as e:
        logger.error(f"Erro ao remover evento: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

@app.route("/api/eventos/busca", methods=["GET"])
def buscar_eventos():
    """
    Search for events by title
    ---
    tags:
      - Events
    parameters:
      - name: titulo
        in: query
        type: string
        required: true
        description: Title to search for
    responses:
      200:
        description: Search results
        schema:
          type: object
          properties:
            success:
              type: boolean
            events:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  title:
                    type: string
                  description:
                    type: string
                  link:
                    type: string
                  event_date:
                    type: string
                    format: date
                  created_at:
                    type: string
                    format: date-time
      400:
        description: Invalid request
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
            error:
              type: string
    """
    try:
        titulo = request.args.get('titulo')
        
        if not titulo:
            return jsonify({
                "success": False,
                "error": "Parâmetro 'titulo' é obrigatório"
            }), 400
            
        events = event_manager.get_events_by_title(titulo)
        
        return jsonify({
            "success": True,
            "events": events
        })
    except Exception as e:
        logger.error(f"Erro ao buscar eventos: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor"
        }), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Recurso não encontrado"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "success": False,
        "error": "Erro interno do servidor"
    }), 500

init_db()

if __name__ == "__main__":
    try:
        db_manager = DatabaseManager()
        # Configura o servidor para aceitar apenas HTTP
        app.run(debug=True, host='0.0.0.0', port=5001, ssl_context=None)
    except Exception as e:
        logger.error(f"Erro ao iniciar o aplicativo: {e}")
    finally:
        try:
            db_manager = DatabaseManager()
            db_manager.close_all_connections()
        except:
            pass