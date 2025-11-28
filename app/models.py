"""
Modelos de la base de datos
"""
from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class TipoDireccion(str, enum.Enum):
    FACTURACION = "FACTURACION"
    ENVIO = "ENVIO"


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    razon_social = Column(String(255), nullable=False)
    nombre_comercial = Column(String(255), nullable=False)
    rfc = Column(String(13), unique=True, nullable=False, index=True)
    correo_electronico = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=False)

    # Relación con domicilios
    domicilios = relationship("Domicilio", back_populates="cliente", cascade="all, delete-orphan")


class Domicilio(Base):
    __tablename__ = "domicilios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    domicilio = Column(String(500), nullable=False)
    colonia = Column(String(255), nullable=False)
    municipio = Column(String(255), nullable=False)
    estado = Column(String(255), nullable=False)
    tipo_direccion = Column(Enum(TipoDireccion), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    # Relación con cliente
    cliente = relationship("Cliente", back_populates="domicilios")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    unidad_medida = Column(String(50), nullable=False)
    precio_base = Column(Float, nullable=False)
