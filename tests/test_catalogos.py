"""
Tests para el módulo de catálogos
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Configurar base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


class TestClientes:
    """Tests para el CRUD de Clientes"""

    def test_crear_cliente(self, client):
        response = client.post(
            "/clientes",
            json={
                "razon_social": "Empresa Test SA de CV",
                "nombre_comercial": "Test Company",
                "rfc": "TEST123456ABC",
                "correo_electronico": "test@empresa.com",
                "telefono": "5551234567"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["razon_social"] == "Empresa Test SA de CV"
        assert "id" in data

    def test_listar_clientes(self, client):
        # Crear cliente primero
        client.post(
            "/clientes",
            json={
                "razon_social": "Empresa Test SA de CV",
                "nombre_comercial": "Test Company",
                "rfc": "TEST123456ABC",
                "correo_electronico": "test@empresa.com",
                "telefono": "5551234567"
            }
        )
        
        response = client.get("/clientes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_obtener_cliente(self, client):
        # Crear cliente
        create_response = client.post(
            "/clientes",
            json={
                "razon_social": "Empresa Test SA de CV",
                "nombre_comercial": "Test Company",
                "rfc": "TEST123456ABC",
                "correo_electronico": "test@empresa.com",
                "telefono": "5551234567"
            }
        )
        cliente_id = create_response.json()["id"]
        
        response = client.get(f"/clientes/{cliente_id}")
        assert response.status_code == 200
        assert response.json()["id"] == cliente_id

    def test_actualizar_cliente(self, client):
        # Crear cliente
        create_response = client.post(
            "/clientes",
            json={
                "razon_social": "Empresa Test SA de CV",
                "nombre_comercial": "Test Company",
                "rfc": "TEST123456ABC",
                "correo_electronico": "test@empresa.com",
                "telefono": "5551234567"
            }
        )
        cliente_id = create_response.json()["id"]
        
        response = client.put(
            f"/clientes/{cliente_id}",
            json={"nombre_comercial": "Updated Company"}
        )
        assert response.status_code == 200
        assert response.json()["nombre_comercial"] == "Updated Company"

    def test_eliminar_cliente(self, client):
        # Crear cliente
        create_response = client.post(
            "/clientes",
            json={
                "razon_social": "Empresa Test SA de CV",
                "nombre_comercial": "Test Company",
                "rfc": "TEST123456ABC",
                "correo_electronico": "test@empresa.com",
                "telefono": "5551234567"
            }
        )
        cliente_id = create_response.json()["id"]
        
        response = client.delete(f"/clientes/{cliente_id}")
        assert response.status_code == 204
        
        # Verificar que ya no existe
        get_response = client.get(f"/clientes/{cliente_id}")
        assert get_response.status_code == 404


class TestProductos:
    """Tests para el CRUD de Productos"""

    def test_crear_producto(self, client):
        response = client.post(
            "/productos",
            json={
                "nombre": "Producto Test",
                "unidad_medida": "PZA",
                "precio_base": 100.50
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Producto Test"
        assert data["precio_base"] == 100.50

    def test_listar_productos(self, client):
        client.post(
            "/productos",
            json={
                "nombre": "Producto Test",
                "unidad_medida": "PZA",
                "precio_base": 100.50
            }
        )
        
        response = client.get("/productos")
        assert response.status_code == 200
        assert len(response.json()) >= 1


class TestDomicilios:
    """Tests para el CRUD de Domicilios"""

    def test_crear_domicilio(self, client):
        # Primero crear un cliente
        cliente_response = client.post(
            "/clientes",
            json={
                "razon_social": "Empresa Test SA de CV",
                "nombre_comercial": "Test Company",
                "rfc": "TEST123456ABC",
                "correo_electronico": "test@empresa.com",
                "telefono": "5551234567"
            }
        )
        cliente_id = cliente_response.json()["id"]
        
        # Crear domicilio
        response = client.post(
            f"/clientes/{cliente_id}/domicilios",
            json={
                "domicilio": "Calle Test 123",
                "colonia": "Centro",
                "municipio": "Guadalajara",
                "estado": "Jalisco",
                "tipo_direccion": "FACTURACION"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["domicilio"] == "Calle Test 123"
        assert data["tipo_direccion"] == "FACTURACION"


class TestHealthCheck:
    """Tests para health check"""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
