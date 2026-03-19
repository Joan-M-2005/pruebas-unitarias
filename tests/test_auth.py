# tests/test_auth.py
import pytest

class TestRegistro:
    def test_registro_exitoso(self, client):
        resp = client.post("/api/auth/registro", json={
            "username": "nuevo_docente",
            "email": "nuevo@uni.mx",
            "password": "Segura123!",
            "rol": "docente"
        })
        assert resp.status_code == 201
        datos = resp.get_json()
        assert "id" in datos
        assert "mensaje" in datos

    def test_username_duplicado(self, client):
        payload = {"username": "duplicado", "email": "a@test.mx", "password": "Pass1234!", "rol": "docente"}
        client.post("/api/auth/registro", json=payload)
        
        # Segundo intento con mismo username pero diferente email
        payload["email"] = "b@test.mx" 
        resp = client.post("/api/auth/registro", json=payload)
        assert resp.status_code == 409

class TestLogin:
    def test_login_exitoso_retorna_token(self, client):
        client.post("/api/auth/registro", json={
            "username": "user_login", "email": "ul@test.mx", "password": "LoginPass1!"
        })
        resp = client.post("/api/auth/login", json={
            "username": "user_login", "password": "LoginPass1!"
        })
        assert resp.status_code == 200
        datos = resp.get_json()
        assert "token" in datos
        assert len(datos["token"]) > 50, "El token debe ser un JWT válido"
        assert datos["tipo"] == "Bearer"
        assert datos["usuario"]["username"] == "user_login"

    def test_password_incorrecta_retorna_401(self, client):
        client.post("/api/auth/registro", json={
            "username": "user_401", "email": "u401@test.mx", "password": "CorrectPass1!"
        })
        resp = client.post("/api/auth/login", json={
            "username": "user_401", "password": "PasswordIncorrecta!"
        })
        assert resp.status_code == 401
        assert "error" in resp.get_json()

    def test_usuario_inexistente_retorna_401(self, client):
        resp = client.post("/api/auth/login", json={
            "username": "noexisto", "password": "cualquiera"
        })
        # IMPORTANTE: Siempre 401, nunca 404 para no confirmar si el usuario existe o no
        assert resp.status_code == 401

class TestRutasProtegidas:
    def test_ruta_protegida_sin_token_retorna_401(self, client):
        # Acceder a una ruta protegida SIN header Authorization
        resp = client.get("/api/auth/perfil") 
        assert resp.status_code == 401

    def test_ruta_protegida_con_token_valido(self, client, auth_headers):
        # auth_headers viene del fixture en conftest.py
        resp = client.get("/api/auth/perfil", headers=auth_headers)
        assert resp.status_code == 200
        assert "usuario" in resp.get_json()

    def test_token_manipulado_retorna_422(self, client):
        # Token JWT manipulado (payload real pero firma cambiada)
        token_falso = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJoYWNrZXIifQ.firma_falsa"
        headers = {"Authorization": f"Bearer {token_falso}"}
        resp = client.get("/api/auth/perfil", headers=headers)
        # Flask-JWT retorna 422 para tokens con formato inválido
        assert resp.status_code in [401, 422]

    def test_header_sin_bearer_retorna_error(self, client):
        headers = {"Authorization": "token_directo_sin_bearer"}
        resp = client.get("/api/auth/perfil", headers=headers)
        assert resp.status_code in [401, 422]

class TestControlDeRoles:
    def test_docente_no_puede_acceder_a_ruta_admin(self, client, auth_headers):
        # Un usuario con rol "docente" NO debe poder acceder a rutas de "admin"
        resp = client.delete("/api/admin/usuarios/1", headers=auth_headers)
        # Esperamos 403 Forbidden (autenticado pero sin permisos)
        assert resp.status_code == 403