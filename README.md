# API de Catálogos

Módulo de catálogos para el sistema de notas de venta. Proporciona CRUD para Clientes, Domicilios y Productos.

## Arquitectura 12 Factores

Este módulo sigue los principios de las aplicaciones de 12 factores:

1. **Codebase**: Un código base rastreado en Git
2. **Dependencies**: Dependencias declaradas explícitamente en `requirements.txt`
3. **Config**: Configuración almacenada en variables de entorno
4. **Backing services**: Base de datos tratada como recurso adjunto
5. **Build, release, run**: Separación estricta entre compilación y ejecución
6. **Processes**: Aplicación stateless
7. **Port binding**: Exporta servicios via binding de puertos
8. **Concurrency**: Escalable horizontalmente
9. **Disposability**: Inicio rápido y apagado graceful
10. **Dev/prod parity**: Paridad entre entornos
11. **Logs**: Logs como streams de eventos
12. **Admin processes**: Procesos admin como procesos one-off

## Endpoints

### Clientes
- `POST /clientes` - Crear cliente
- `GET /clientes` - Listar clientes
- `GET /clientes/{id}` - Obtener cliente
- `PUT /clientes/{id}` - Actualizar cliente
- `DELETE /clientes/{id}` - Eliminar cliente

### Domicilios
- `POST /clientes/{id}/domicilios` - Crear domicilio
- `GET /clientes/{id}/domicilios` - Listar domicilios del cliente
- `GET /domicilios/{id}` - Obtener domicilio
- `PUT /domicilios/{id}` - Actualizar domicilio
- `DELETE /domicilios/{id}` - Eliminar domicilio

### Productos
- `POST /productos` - Crear producto
- `GET /productos` - Listar productos
- `GET /productos/{id}` - Obtener producto
- `PUT /productos/{id}` - Actualizar producto
- `DELETE /productos/{id}` - Eliminar producto

## Métricas

Este módulo implementa métricas de CloudWatch:

1. **RequestLatency**: Tiempo de ejecución de cada endpoint (ms)
2. **HTTPStatusCount**: Conteo de respuestas por rango (2xx, 4xx, 5xx)

Las métricas incluyen dimensión de ambiente (local/production).

## Ejecución Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Ejecutar
uvicorn app.main:app --reload
```

## Docker

```bash
# Construir imagen
docker build -t catalogos-api .

# Ejecutar contenedor
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e ENVIRONMENT=production \
  -e AWS_REGION=us-east-1 \
  catalogos-api
```

## Tests

```bash
pip install pytest pytest-cov httpx
pytest tests/ -v --cov=app
```

## CI/CD

El pipeline de GitHub Actions:
1. Ejecuta tests en cada PR
2. Construye y sube imagen a ECR en push a main
3. Despliega automáticamente a ECS
# Test pipeline
