from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum



# -------------------------------
# 🔹 Server Schema 
# -------------------------------

class ServerCreate(BaseModel):
    name: str = Field(..., title="Server Name", description="The name of the server")

# 🔹 Schema to Responder with a Server created

class ServerResponse(BaseModel):
    ulid: str
    name: str

    class Config:
        orm_mode = True #



# 🔹 Schema para o payload do `POST /data`
class SensorDataCreate(BaseModel):
    server_ulid: str = Field(..., title="Server ULID", description="Unique identifier of the server")
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    voltage: Optional[float] = None
    current: Optional[float] = None

    class Config:
        orm_mode = True
        
# 🔹 Schema para resposta do `GET /data`
class SensorDataResponse(BaseModel):
    id:str
    server_ulid: str
    timestamp: datetime
    temperature: Optional[float]
    humidity: Optional[float]
    voltage: Optional[float]
    current: Optional[float]

    class Config:
        orm_mode = True

# -------------------------------
# 🔹 Users Schema  
# -------------------------------

# Schema para criação de usuário
class UserCreate(BaseModel):
    username: str
    password: str

# Schema para resposta ao registrar um usuário
class UserResponse(BaseModel):
    id: str
    username: str

    class Config:
            orm_mode= True

# Schema para login
class UserLogin(BaseModel):
    username: str
    password: str

# Schema para resposta do JWT Token
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

#Schema for the Healthy Response Sever

class ServerStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class ServerHealthResponse(BaseModel):
    server_ulid: str
    status: ServerStatus
    server_name: str
    
    class Config:
            orm_mode= True


