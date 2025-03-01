import pytest
import random
import string
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Server, SensorData
from app.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import ulid


# Função para gerar um nome aleatório para o servidor
def generate_random_name(prefix="server_"):
    return f"{prefix}{ulid.new()}"

# Função para gerar uma senha aleatória
def generate_random_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

# Função para gerar um nome de usuário aleatório
def generate_random_username():
    return f"user_{ulid.new()}"

# Função para gerar dados aleatórios de sensores
def generate_random_sensor_data(server_ulid):
    return {
        "server_ulid": server_ulid,
        "temperature": random.uniform(20.0, 30.0),
        "humidity": random.uniform(50.0, 80.0),
        "voltage": random.uniform(210.0, 240.0),
        "current": random.uniform(0.5, 2.0)
    }

# Fixture para o TestClient - Escopo de função (será executada a cada teste)
@pytest.fixture(scope="function")
def client():
    return TestClient(app)

# Fixture para criar e autenticar o usuário - Escopo de função
@pytest.fixture(scope="function")
def login_user(client):
    username = generate_random_username()
    password = generate_random_password()
    user_data = {"username": username, "password": password}
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Login para pegar o token
    login_response = client.post("/auth/login", json={"username": username, "password": password})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return token, username

# Fixture para criar servidor - Escopo de função
@pytest.fixture(scope="function")
def create_server(client, login_user):
    token, _ = login_user
    # Nome aleatório do servidor
    server_name = generate_random_name()
    server_data = {"name": server_name}
    response = client.post("/servers/", json=server_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    return response.json()  # Retorna o servidor criado

# Fixture para criar dados de sensores - Escopo de função
@pytest.fixture(scope="function")
def create_sensor_data(client, create_server): #, login_user):
    #token, _ = login_user
    server_ulid = create_server["ulid"]
    
    # Criando dados aleatórios do sensor
    sensor_data = generate_random_sensor_data(server_ulid)
    response = client.post("/data", json=sensor_data)
    assert response.status_code == 201
    return response.json()  # Retorna o sensor data criado

# Teste para verificar a criação de dados de sensores e a obtenção com filtros e agregação
def test_register_and_get_sensor_data(client, create_server, create_sensor_data):
    #token, _ = login_user
    server_ulid = create_server["ulid"]
    
    # Teste sem filtros
    response = client.get(f"/data?server_ulid={server_ulid}")
    assert response.status_code == 200
    assert len(response.json()) > 0  # Deve retornar ao menos um dado

    # Teste com filtro de timestamp (por exemplo, 1 hora atrás)
    start_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    end_time = datetime.utcnow().isoformat()
    response = client.get(f"/data?server_ulid={server_ulid}&start_time={start_time}&end_time={end_time}",
                          )
    assert response.status_code == 200
    assert len(response.json()) > 0  # Deve retornar ao menos um dado dentro do intervalo

    # Teste com agregação (por exemplo, "hour")
    response = client.get(f"/data?server_ulid={server_ulid}&aggregation=hour")
    assert response.status_code == 200
    assert len(response.json()) > 0  # Deve retornar dados agregados

# Teste para verificar a resposta quando não há dados de sensores
def test_get_no_sensor_data(client, login_user):
    token, _ = login_user
    
    # Criar servidor sem dados de sensor
    server_name = generate_random_name()
    server_data = {"name": server_name}
    response = client.post("/servers/", json=server_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    server_ulid = response.json()["ulid"]
    
    # Teste se a rota retorna 404 se não houver dados
    response = client.get(f"/data?server_ulid={server_ulid}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "No sensor data found"


# Cleanup: Apagar os dados criados após os testes
@pytest.fixture(scope="function", autouse=True)
def cleanup_data(client, login_user, create_server, create_sensor_data):
    yield  # Executa o teste
    # Apagar o servidor e o usuário criado após os testes
    db: Session = next(get_db())
    token, _ = login_user
    
    # Apagar servidor criado
    server_ulid = create_server["ulid"]
    server = db.query(Server).filter(Server.ulid == server_ulid).first()
    if server:
        db.delete(server)
        db.commit()

    # Apagar os dados do sensor
    sensor_data = db.query(SensorData).filter(SensorData.server_ulid == server_ulid).all()
    for data in sensor_data:
        db.delete(data)
        db.commit()

    # Apagar o usuário criado
    user = db.query(User).filter(User.username == create_server["name"]).first()
    if user:
        db.delete(user)
        db.commit()
