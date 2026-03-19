import pytest
from app import create_app, db as _db
from app.models.estudiante import Estudiante
from app.models.usuario import Usuario
from app.config import TestingConfig

# Fixture: Aplicación de prueba
@pytest.fixture(scope="session")
def app():
    """Crea la aplicación Flask en modo de pruebas."""
    app = create_app(TestingConfig)
    yield app

# Fixture: Base de datos (MODIFICADO: Se destruye y recrea en CADA prueba)
@pytest.fixture(scope="function", autouse=True)
def db(app):
    """Crea las tablas en la BD de prueba (SQLite en memoria)."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()

# Fixture: Transacción limpia por prueba (Simplificado)
@pytest.fixture(scope="function")
def session(db):
    yield db.session

# Fixture: Cliente HTTP de prueba
@pytest.fixture(scope="function")
def client(app):
    """Cliente HTTP que simula peticiones a la API."""
    return app.test_client()

# Fixture: Estudiante de prueba
@pytest.fixture
def estudiante_data():
    """Datos válidos de un estudiante para reutilizar en pruebas."""
    return {
        "matricula": "TEST001",
        "nombre": "Carlos",
        "apellido": "Ramirez",
        "email": "carlos@test.edu.mx",
        "carrera": "ITIC",
        "semestre": 5
    }

# Fixture: Token JWT de prueba
@pytest.fixture
def auth_headers(client):
    """Genera un token JWT válido para pruebas de rutas protegidas."""
    client.post("/api/auth/registro", json={
        "username": "docente_test", 
        "email": "doc@test.mx",
        "password": "Password123!", 
        "rol": "docente"
    })
    resp = client.post("/api/auth/login", json={
        "username": "docente_test", 
        "password": "Password123!"
    })
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}