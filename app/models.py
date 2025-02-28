from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.database import Base
import datetime
import ulid
import enum



class Server(Base):
    """
    Representa um servidor on-premise que coleta dados de sensores.
    Cada servidor pode ter até 4 sensores (um de cada tipo).
    """
    __tablename__ = "servers"

    ulid = Column(String, primary_key=True, nullable=False, unique=True, index=True)
    name = Column(String, unique=True, nullable=False)

    # Relacionamento: um servidor pode ter vários sensores, mas no máximo um de cada tipo
    sensor_data = relationship("SensorData", back_populates="server", cascade="all, delete-orphan")



class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(String, primary_key=True, default=lambda: str(ulid.new()), index=True)  
    server_ulid = Column(String, ForeignKey("servers.ulid"), nullable=False)
    timestamp = Column(DateTime, nullable=False) 
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    voltage = Column(Float, nullable=True)
    current = Column(Float, nullable=True)

    server = relationship("Server", back_populates="sensor_data")

# -------------------------------
class User(Base):
    """
    Representa um usuário autenticado que pode acessar a API.
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(ulid.new()))
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

