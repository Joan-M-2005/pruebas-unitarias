from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import DevelopmentConfig
from flasgger import Swagger

# 1. Creamos la instancia de la base de datos ANTES de cualquier otra cosa
db = SQLAlchemy()

def create_app(config=DevelopmentConfig):
    """Patrón Application Factory: crea y configura la app Flask."""
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config)
    
    # Inicializar extensiones con la app
    db.init_app(app)
    CORS(app)
    jwt = JWTManager(app)

    # --- TODO ESTO DEBE IR ADENTRO DE LA FUNCIÓN (Indentado) ---
    swagger_config = {
        "headers": [],
        "specs": [{"endpoint": "apispec", "route": "/apispec.json"}],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/" # La documentación estará en /docs/
    }
    
    swagger_template = {
        "info": {
            "title": "API Escolar ITIC",
            "version": "1.0.0",
            "description": "API REST para gestión escolar"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header"
            }
        }
    }
    
    # ESTA ES LA LÍNEA QUE FALTABA PARA INICIALIZAR SWAGGER
    Swagger(app, config=swagger_config, template=swagger_template)
    # -----------------------------------------------------------
    
    # 2. ¡IMPORTANTE! Las importaciones de rutas van AQUÍ ADENTRO de la función
    from .routes import main_bp
    from .routes.estudiantes import estudiantes_bp
    from .routes.calificaciones import cal_bp
    from .routes.auth import auth_bp
    from .routes.ordenes import ordenes_bp
    from .routes.materias import materias_bp
    
    # Registrar rutas (blueprints)
    app.register_blueprint(main_bp)
    app.register_blueprint(estudiantes_bp)
    app.register_blueprint(cal_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(ordenes_bp)
    app.register_blueprint(materias_bp)
    
    return app