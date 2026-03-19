# tests/test_calificaciones.py
import pytest

class TestRegistroCalificaciones:
    @pytest.fixture(autouse=True)
    def setup(self, client, auth_headers, estudiante_data):
        # Crear estudiante
        resp_est = client.post("/api/estudiantes/", json=estudiante_data)
        self.id_estudiante = resp_est.get_json()["estudiante"]["id"]
        
        # Crear materia
        resp_mat = client.post("/api/materias/", json={
            "clave": "PROG101", "nombre": "Programación Web",
            "creditos": 5, "docente": "Dr. Test"
        }, headers=auth_headers)
        self.id_materia = resp_mat.get_json()["materia"]["id"]
        
        self.client = client
        self.auth_headers = auth_headers

    def test_registrar_calificacion_valida(self):
        resp = self.client.post("/api/calificaciones/", json={
            "estudiante_id": self.id_estudiante,
            "materia_id": self.id_materia,
            "calificacion": 87.5,
            "periodo": "2024-1"
        })
        assert resp.status_code == 201
        datos = resp.get_json()
        assert datos["calificacion"] == 87.5
        assert datos["aprobado"] == True

    @pytest.mark.parametrize("cal_invalida", [-1, 100.1, 200, -50])
    def test_calificacion_fuera_de_rango(self, cal_invalida):
        resp = self.client.post("/api/calificaciones/", json={
            "estudiante_id": self.id_estudiante,
            "materia_id": self.id_materia,
            "calificacion": cal_invalida,
            "periodo": "2024-1"
        })
        assert resp.status_code == 400

    def test_calificacion_exactamente_cero(self):
        resp = self.client.post("/api/calificaciones/", json={
            "estudiante_id": self.id_estudiante,
            "materia_id": self.id_materia,
            "calificacion": 0,
            "periodo": "2024-1"
        })
        assert resp.status_code == 201
        assert resp.get_json()["aprobado"] == False

    def test_calificacion_exactamente_cien(self):
        resp = self.client.post("/api/calificaciones/", json={
            "estudiante_id": self.id_estudiante,
            "materia_id": self.id_materia,
            "calificacion": 100,
            "periodo": "2024-1"
        })
        assert resp.status_code == 201
        assert resp.get_json()["aprobado"] == True

class TestKardex:
    def test_kardex_calcula_promedio_correctamente(self, client, auth_headers, estudiante_data):
        id_est = client.post("/api/estudiantes/", json=estudiante_data).get_json()["estudiante"]["id"]
        
        calificaciones_a_registrar = [
            ("MAT101", "Matemáticas", 80),
            ("FIS101", "Fisica", 90),
            ("QUI101", "Quimica", 70)
        ]
        
        for clave, nombre, cal in calificaciones_a_registrar:
            mat = client.post("/api/materias/", json={
                "clave": clave, "nombre": nombre, "creditos": 4
            }, headers=auth_headers).get_json()["materia"]
            
            client.post("/api/calificaciones/", json={
                "estudiante_id": id_est,
                "materia_id": mat["id"],
                "calificacion": cal,
                "periodo": "2024-1"
            })
            
        resp = client.get(f"/api/estudiantes/{id_est}/kardex")
        assert resp.status_code == 200
        
        kardex = resp.get_json()
        estadisticas = kardex["estadisticas"]
        
        assert estadisticas["promedio_general"] == 80.0
        assert estadisticas["total_materias"] == 3
        assert estadisticas["materias_aprobadas"] == 3
        assert estadisticas["materias_reprobadas"] == 0
        assert estadisticas["calificacion_maxima"] == 90
        assert estadisticas["calificacion_minima"] == 70

    def test_kardex_detecta_estatus_en_riesgo(self, client, auth_headers, estudiante_data):
        id_est = client.post("/api/estudiantes/", json=estudiante_data).get_json()["estudiante"]["id"]
        
        mat = client.post("/api/materias/", json={
            "clave": "REP101", "nombre": "Reprobada", "creditos": 3
        }, headers=auth_headers).get_json()["materia"]
        
        client.post("/api/calificaciones/", json={
            "estudiante_id": id_est, "materia_id": mat["id"],
            "calificacion": 50, "periodo": "2024-1"
        })
        
        kardex = client.get(f"/api/estudiantes/{id_est}/kardex").get_json()
        assert kardex["estadisticas"]["estatus"] == "En riesgo"
        assert kardex["estadisticas"]["materias_reprobadas"] == 1

    def test_kardex_sin_calificaciones(self, client, estudiante_data):
        id_est = client.post("/api/estudiantes/", json=estudiante_data).get_json()["estudiante"]["id"]
        resp = client.get(f"/api/estudiantes/{id_est}/kardex")
        
        assert resp.status_code == 200
        datos = resp.get_json()
        assert datos["calificaciones"] == []
        assert "mensaje" in datos
        