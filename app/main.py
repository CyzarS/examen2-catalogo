"""
Módulo de Catálogos - API REST
CRUD de Clientes, Domicilios y Productos
"""
import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import boto3
from botocore.exceptions import ClientError

from app.database import engine, get_db, Base
from app.models import Cliente, Domicilio, Producto
from app.schemas import (
    ClienteCreate, ClienteUpdate, ClienteResponse,
    DomicilioCreate, DomicilioUpdate, DomicilioResponse,
    ProductoCreate, ProductoUpdate, ProductoResponse
)
from app.metrics import MetricsCollector

# Configuración del ambiente
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Inicializar métricas
metrics = MetricsCollector(
    namespace="CatalogosAPI",
    environment=ENVIRONMENT,
    region=AWS_REGION
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown

app = FastAPI(
    title="API de Catálogos",
    description="CRUD de Clientes, Domicilios y Productos",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para métricas de tiempo de respuesta
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000  # Convertir a milisegundos
    
    # Registrar métricas
    endpoint = f"{request.method} {request.url.path}"
    status_code = response.status_code
    
    # Métrica de tiempo de ejecución
    metrics.record_latency(endpoint, duration)
    
    # Métrica de comportamiento por rango de status
    metrics.record_http_status(endpoint, status_code)
    
    return response

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": ENVIRONMENT}

# ==================== CRUD CLIENTES ====================

@app.post("/clientes", response_model=ClienteResponse, status_code=201)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Crear un nuevo cliente"""
    db_cliente = Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@app.get("/clientes", response_model=list[ClienteResponse])
def listar_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todos los clientes"""
    clientes = db.query(Cliente).offset(skip).limit(limit).all()
    return clientes

@app.get("/clientes/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtener un cliente por ID"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.put("/clientes/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(cliente_id: int, cliente: ClienteUpdate, db: Session = Depends(get_db)):
    """Actualizar un cliente"""
    db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    for key, value in cliente.model_dump(exclude_unset=True).items():
        setattr(db_cliente, key, value)
    
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@app.delete("/clientes/{cliente_id}", status_code=204)
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Eliminar un cliente"""
    db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    db.delete(db_cliente)
    db.commit()
    return None

# ==================== CRUD DOMICILIOS ====================

@app.post("/clientes/{cliente_id}/domicilios", response_model=DomicilioResponse, status_code=201)
def crear_domicilio(cliente_id: int, domicilio: DomicilioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo domicilio para un cliente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    db_domicilio = Domicilio(**domicilio.model_dump(), cliente_id=cliente_id)
    db.add(db_domicilio)
    db.commit()
    db.refresh(db_domicilio)
    return db_domicilio

@app.get("/clientes/{cliente_id}/domicilios", response_model=list[DomicilioResponse])
def listar_domicilios(cliente_id: int, db: Session = Depends(get_db)):
    """Listar domicilios de un cliente"""
    domicilios = db.query(Domicilio).filter(Domicilio.cliente_id == cliente_id).all()
    return domicilios

@app.get("/domicilios/{domicilio_id}", response_model=DomicilioResponse)
def obtener_domicilio(domicilio_id: int, db: Session = Depends(get_db)):
    """Obtener un domicilio por ID"""
    domicilio = db.query(Domicilio).filter(Domicilio.id == domicilio_id).first()
    if not domicilio:
        raise HTTPException(status_code=404, detail="Domicilio no encontrado")
    return domicilio

@app.put("/domicilios/{domicilio_id}", response_model=DomicilioResponse)
def actualizar_domicilio(domicilio_id: int, domicilio: DomicilioUpdate, db: Session = Depends(get_db)):
    """Actualizar un domicilio"""
    db_domicilio = db.query(Domicilio).filter(Domicilio.id == domicilio_id).first()
    if not db_domicilio:
        raise HTTPException(status_code=404, detail="Domicilio no encontrado")
    
    for key, value in domicilio.model_dump(exclude_unset=True).items():
        setattr(db_domicilio, key, value)
    
    db.commit()
    db.refresh(db_domicilio)
    return db_domicilio

@app.delete("/domicilios/{domicilio_id}", status_code=204)
def eliminar_domicilio(domicilio_id: int, db: Session = Depends(get_db)):
    """Eliminar un domicilio"""
    db_domicilio = db.query(Domicilio).filter(Domicilio.id == domicilio_id).first()
    if not db_domicilio:
        raise HTTPException(status_code=404, detail="Domicilio no encontrado")
    
    db.delete(db_domicilio)
    db.commit()
    return None

# ==================== CRUD PRODUCTOS ====================

@app.post("/productos", response_model=ProductoResponse, status_code=201)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo producto"""
    db_producto = Producto(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

@app.get("/productos", response_model=list[ProductoResponse])
def listar_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todos los productos"""
    productos = db.query(Producto).offset(skip).limit(limit).all()
    return productos

@app.get("/productos/{producto_id}", response_model=ProductoResponse)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """Obtener un producto por ID"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@app.put("/productos/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(producto_id: int, producto: ProductoUpdate, db: Session = Depends(get_db)):
    """Actualizar un producto"""
    db_producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    for key, value in producto.model_dump(exclude_unset=True).items():
        setattr(db_producto, key, value)
    
    db.commit()
    db.refresh(db_producto)
    return db_producto

@app.delete("/productos/{producto_id}", status_code=204)
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    """Eliminar un producto"""
    db_producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(db_producto)
    db.commit()
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
