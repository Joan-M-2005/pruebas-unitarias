# Pruebas Unitarias y E2E para API REST con Flask

Este repositorio contiene la implementación de un entorno de pruebas profesional para una API REST construida con **Python y Flask**. El objetivo de este proyecto es garantizar la calidad, seguridad y fiabilidad del software mediante pruebas automatizadas.

Se logró una **cobertura de código del 89.22%**, superando el estándar de la industria.

---

## Tecnologías y Herramientas de Testing
* **Framework de Pruebas:** Pytest
* **Simulación HTTP:** Pytest-Flask
* **Base de Datos de Pruebas:** SQLite en memoria (aislada de producción)
* **Medición de Cobertura:** Pytest-cov

---

## Tipos de Pruebas Implementadas

1. **Pruebas Unitarias (Modelos):** * Verificación de hashing de contraseñas de usuarios.
   * Validación de campos y valores por defecto.
2. **Pruebas de Integración (CRUD y Endpoints):** * Manejo de peticiones válidas e inválidas (400, 404, 409).
   * Cálculos estadísticos complejos (Generación de Kardex y promedios).
3. **Pruebas de Seguridad (JWT):** * Simulación de ataques con tokens manipulados o expirados.
   * Control de acceso basado en roles (RBAC).
4. **Pruebas End-to-End (E2E):** * Simulación de un flujo completo: un administrador crea productos, un cliente se registra, realiza una compra y el sistema descuenta el inventario correctamente mediante transacciones atómicas (Commit/Rollback).

---

## Reporte de Cobertura (Coverage)

Se utilizó la directiva `pytest --cov=app` para medir qué porcentaje del código fue puesto a prueba, obteniendo resultados sobresalientes en los módulos de rutas y base de datos.

![Reporte de Cobertura Pytest](img/cobertura.png)
*(Aquí se muestra el reporte generado en HTML por pytest-cov)*