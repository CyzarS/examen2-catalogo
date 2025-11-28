"""
Schemas de Pydantic para validación de datos
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class TipoDireccion(str, Enum):
    FACTURACION = "FACTURACION"
    ENVIO = "ENVIO"


# ==================== CLIENTE SCHEMAS ====================

class ClienteBase(BaseModel):
    razon_social: str = Field(..., min_length=1, max_length=255)
    nombre_comercial: str = Field(..., min_length=1, max_length=255)
    rfc: str = Field(..., min_length=12, max_length=13, pattern=r'^[A-ZÑ&]{3,4}\d{6}[A-Z\d]{3}$')
    correo_electronico: EmailStr
    telefono: str = Field(..., min_length=10, max_length=20)


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    razon_social: Optional[str] = Field(None, min_length=1, max_length=255)
    nombre_comercial: Optional[str] = Field(None, min_length=1, max_length=255)
    rfc: Optional[str] = Field(None, min_length=12, max_length=13)
    correo_electronico: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, min_length=10, max_length=20)


class ClienteResponse(ClienteBase):
    id: int

    class Config:
        from_attributes = True


# ==================== DOMICILIO SCHEMAS ====================

class DomicilioBase(BaseModel):
    domicilio: str = Field(..., min_length=1, max_length=500)
    colonia: str = Field(..., min_length=1, max_length=255)
    municipio: str = Field(..., min_length=1, max_length=255)
    estado: str = Field(..., min_length=1, max_length=255)
    tipo_direccion: TipoDireccion


class DomicilioCreate(DomicilioBase):
    pass


class DomicilioUpdate(BaseModel):
    domicilio: Optional[str] = Field(None, min_length=1, max_length=500)
    colonia: Optional[str] = Field(None, min_length=1, max_length=255)
    municipio: Optional[str] = Field(None, min_length=1, max_length=255)
    estado: Optional[str] = Field(None, min_length=1, max_length=255)
    tipo_direccion: Optional[TipoDireccion] = None


class DomicilioResponse(DomicilioBase):
    id: int
    cliente_id: int

    class Config:
        from_attributes = True


# ==================== PRODUCTO SCHEMAS ====================

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    unidad_medida: str = Field(..., min_length=1, max_length=50)
    precio_base: float = Field(..., gt=0)


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    unidad_medida: Optional[str] = Field(None, min_length=1, max_length=50)
    precio_base: Optional[float] = Field(None, gt=0)


class ProductoResponse(ProductoBase):
    id: int

    class Config:
        from_attributes = True
