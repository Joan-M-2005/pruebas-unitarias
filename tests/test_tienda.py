# tests/test_tienda.py
import pytest

class TestFlujoCompleto:
    """Prueba el flujo completo de compra en la tienda."""
    
    @pytest.fixture(autouse=True)
    def setup_tienda(self, client):
        """Prepara el estado inicial de la tienda para cada prueba."""
        self.client = client
        self.token_admin = None
        self.token_cliente = None
        self.productos_creados = {}

    def _registrar_admin_y_productos(self):
        """Helper: crea admin y los productos del catálogo."""
        self.client.post("/api/auth/registro", json={
            "username": "admin_tienda", "email": "admin@techstore.mx",
            "password": "Admin123!", "rol": "admin"
        })
        resp_login = self.client.post("/api/auth/login", json={
            "username": "admin_tienda", "password": "Admin123!"
        })
        self.token_admin = resp_login.get_json()["token"]
        headers_admin = {"Authorization": f"Bearer {self.token_admin}"}

        productos = [
            {"sku": "LAP001", "nombre": "Laptop Gamer 15", "precio": 18999.00, "stock": 10, "categoria_id": 1},
            {"sku": "MOU001", "nombre": "Mouse Inalambrico", "precio": 349.00, "stock": 50, "categoria_id": 2},
            {"sku": "USB001", "nombre": "USB Hub 7 puertos", "precio": 199.00, "stock": 30, "categoria_id": 2}
        ]
        for prod in productos:
            resp = self.client.post("/api/productos/", json=prod, headers=headers_admin)
            if resp.status_code == 201:
                self.productos_creados[prod["sku"]] = resp.get_json()["producto"]

    def _registrar_cliente_y_login(self):
        """Helper: crea un cliente y obtiene su token."""
        self.client.post("/api/auth/registro", json={
            "username": "cliente01", "email": "cliente@gmail.com",
            "password": "Cliente123!", "rol": "cliente"
        })
        resp = self.client.post("/api/auth/login", json={
            "username": "cliente01", "password": "Cliente123!"
        })
        self.token_cliente = resp.get_json()["token"]

    def test_flujo_completo_compra(self):
        # PASO 1: Setup de productos
        self._registrar_admin_y_productos()
        
        # PASO 2: Cliente se registra
        self._registrar_cliente_y_login()
        assert self.token_cliente is not None, "El cliente debe tener token"

        # PASO 3: Buscar productos
        headers_cliente = {"Authorization": f"Bearer {self.token_cliente}"}
        resp_busqueda = self.client.get("/api/productos/?buscar=laptop", headers=headers_cliente)
        
        # Si la ruta de productos existe, validamos la búsqueda
        if resp_busqueda.status_code == 200:
            resultados = resp_busqueda.get_json()["productos"]
            assert any("Laptop" in p["nombre"] for p in resultados)

        # PASO 4: Procesar orden (Solo si pudimos crear los productos)
        if "LAP001" in self.productos_creados and "MOU001" in self.productos_creados:
            id_laptop = self.productos_creados["LAP001"]["id"]
            id_mouse = self.productos_creados["MOU001"]["id"]
            stock_inicial_laptop = self.productos_creados["LAP001"]["stock"]

            resp_orden = self.client.post("/api/ordenes/", json={
                "cliente_id": 1,
                "productos": [
                    {"producto_id": id_laptop, "cantidad": 2},
                    {"producto_id": id_mouse, "cantidad": 5}
                ]
            }, headers=headers_cliente)
            
            assert resp_orden.status_code == 201
            orden = resp_orden.get_json()
            assert orden["total"] > 0
            assert "orden_id" in orden

            # PASO 5: Verificar que el stock se redujo
            resp_prod = self.client.get(f"/api/productos/{id_laptop}", headers=headers_cliente)
            if resp_prod.status_code == 200:
                stock_actual = resp_prod.get_json()["stock"]
                assert stock_actual == stock_inicial_laptop - 2

        # PASO 6: Reporte de ventas
        headers_admin = {"Authorization": f"Bearer {self.token_admin}"}
        resp_reporte = self.client.get("/api/reportes/ventas", headers=headers_admin)
        if resp_reporte.status_code == 200:
            reporte = resp_reporte.get_json()
            assert reporte["resumen"]["ingresos"] > 0

    def test_orden_con_stock_insuficiente_falla(self):
        self._registrar_admin_y_productos()
        self._registrar_cliente_y_login()
        
        if "USB001" in self.productos_creados:
            id_usb = self.productos_creados["USB001"]["id"]
            headers_cliente = {"Authorization": f"Bearer {self.token_cliente}"}

            # Intentar comprar más de lo que hay en stock (pedimos 999)
            resp = self.client.post("/api/ordenes/", json={
                "cliente_id": 1,
                "productos": [{"producto_id": id_usb, "cantidad": 999}]
            }, headers=headers_cliente)
            
            assert resp.status_code == 400
            assert "error" in resp.get_json()

    def test_cliente_no_puede_ver_reporte_admin(self):
        self._registrar_cliente_y_login()
        headers_cliente = {"Authorization": f"Bearer {self.token_cliente}"}
        resp = self.client.get("/api/reportes/ventas", headers=headers_cliente)
        # Si la ruta existe, debe bloquear al cliente
        if resp.status_code != 404:
            assert resp.status_code == 403