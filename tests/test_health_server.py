import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Server, SensorData
from app.database import get_db
from sqlalchemy.orm import Session
import ulid
from datetime import datetime, timedelta

# Definindo a fixture para o TestClient
@pytest.fixture
def client():
    return TestClient(app)

# Função para gerar um nome de usuário aleatório
def generate_random_username():
    return f"testuser_{ulid.new()}"

# Função para gerar uma senha aleatória
def generate_random_password():
    return 'validpassword123'

# Função para gerar um nome de servidor aleatório
def generate_random_server_name():
    return f"TestServer_{ulid.new()}"

# Função para gerar dados de sensor aleatórios
def generate_random_sensor_data(server_ulid):
    return {
        "server_ulid": server_ulid,
        "temperature": 22.5,
        "humidity": 60.0,
        "voltage": 220.0,
        "current": 1.5
    }

# Função para criar um usuário e retornar o token JWT
@pytest.fixture
def login_user(client):
    username = generate_random_username()
    password = generate_random_password()
    user_data = {"username": username, "password": password}
    
    # Criação do usuário
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Login para pegar o token
    login_response = client.post("/auth/login", json={"username": username, "password": password})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    yield token, username  # Retorna o token e o nome do usuário para ser utilizado nos testes

    # Cleanup: Deletar o usuário e dados após o teste
    db: Session = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    if user:
        db.delete(user)
        db.commit()

# Teste 1: Usuário autenticado com servidores ativos
def test_get_all_servers_health(client, login_user):
    token, username = login_user

    # Criar servidor no banco de dados
    server_name = generate_random_server_name()
    server_data = {"name": server_name}
    response = client.post("/servers/", json=server_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201

    server_ulid = response.json()["ulid"]

    # Adicionar um dado de sensor
    sensor_data = generate_random_sensor_data(server_ulid)
    response = client.post("/data", json=sensor_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201

    # Chama a rota /health/all
    response = client.get("/health/all", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    health_statuses = response.json()
    assert len(health_statuses) > 0
    assert health_statuses[0]["status"] == "online"  # Status deve ser "online" devido ao dado de sensor

    # Cleanup: Deletar o servidor e o dado de sensor
    db: Session = next(get_db())
    server = db.query(Server).filter(Server.ulid == server_ulid).first()
    if server:
        db.delete(server)
        db.commit()

# Teste 2: Usuário autenticado sem servidores registrados
def test_get_all_servers_health(client, login_user):
    token, username = login_user

    # Criar servidor no banco de dados
    server_name = generate_random_server_name()
    server_data = {"name": server_name}
    response = client.post("/servers/", json=server_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201  # Espera 201 para a criação do servidor

    server_ulid = response.json()["ulid"]

    # Adicionar um dado de sensor
    sensor_data = generate_random_sensor_data(server_ulid)
    response = client.post("/data", json=sensor_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201  # Espera 201 para a criação dos dados do sensor

    # Verificar o status de todos os servidores
    response = client.get("/health/all", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200  # Espera 200 para a verificação de status dos servidores
