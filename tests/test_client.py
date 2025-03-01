import random
import string
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User
from app.database import get_db
from sqlalchemy.orm import Session


client = TestClient(app)

# Função para gerar nome de usuário aleatório
def generate_random_username():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

# Função para gerar senha aleatória
def generate_random_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

# Test for POST /auth/register - Success
@pytest.fixture
def create_user():
    # Gerar usuário e senha aleatórios
    username = generate_random_username()
    password = generate_random_password()
    data = {"username": username, "password": password}

    # Criar o usuário
    response = client.post("/auth/register", json=data)
    yield response, username, password  # Retorna o usuário criado e dados

    # Deletar o usuário após o teste
    db: Session = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    if user:
        db.delete(user)
        db.commit()

# Test for POST /auth/register - Success
def test_register_user_success(create_user):
    response, username, password = create_user

    # Verifica se o status code da resposta é 201 (Created)
    assert response.status_code == 201
    response_data = response.json()

    # Verifica se os dados retornados são válidos
    assert "id" in response_data
    assert "username" in response_data
    assert response_data["username"] == username

# Test for POST /auth/register - Conflict (username already exists)
def test_register_user_conflict(create_user):
    response, username, password = create_user

    # Tenta criar o mesmo usuário novamente
    data = {"username": username, "password": password}
    response = client.post("/auth/register", json=data)

    # Verifica se o status code é 409 (Conflict)
    assert response.status_code == 409
    assert response.json()["detail"] == "Username already registered"

# Test for POST /auth/register - Password too short
def test_register_user_short_password():
    username = generate_random_username()
    data = {
        "username": username,
        "password": "short"
    }

    response = client.post("/auth/register", json=data)

    # Verifica se o status code é 400 (Bad Request)
    assert response.status_code == 400
    assert response.json()["detail"] == "Password must be at least 8 characters long"
