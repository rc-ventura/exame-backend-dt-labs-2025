# exame-backend-dt-labs-2025

# Projeto Exemplo: API de Sensor com Cache, Filas e PostgreSQL

Este é um projeto de uma API criada com FastAPI para gerenciar dados de sensores, utilizando **Redis** para cache e **PostgreSQL** como banco de dados. O projeto também faz uso de **Docker** e **Docker Compose** para facilitar a configuração e o gerenciamento dos contêineres.

## Tecnologias Utilizadas

- **FastAPI**: Framework para construção de APIs assíncronas em Python.
- **PostgreSQL**: Sistema de gerenciamento de banco de dados relacional.
- **Redis**: Armazenamento de dados em memória, usado aqui para cache.
- **Docker**: Ferramenta para criar e gerenciar contêineres.
- **Docker Compose**: Utilizado para orquestrar os contêineres Docker.
- **SQLAlchemy**: ORM (Object Relational Mapper) para interagir com o banco de dados PostgreSQL.
- **Pydantic**: Biblioteca para validação de dados com base em modelos.
- **pytest**: Framework de testes para validar a funcionalidade da API.

## Funcionalidades Implementadas

### 1. **Cadastro de Dados de Sensores**
- Rota `POST /data`: Recebe dados de sensores (temperatura, umidade, voltagem, corrente) e os armazena no banco de dados.

### 2. **Consulta de Dados de Sensores**
- Rota `GET /data`: Recupera dados de sensores com possibilidade de filtrar por servidor e por intervalo de tempo.
- Rota `GET /data?aggregation={level}`: Permite a agregação dos dados em diferentes granularidades (por minuto, hora ou dia).
  
### 3. **Cache com Redis**
- Rota `POST /cache/set`: Armazena dados em cache (utilizando Redis) com uma chave e um valor.
- Rota `GET /cache/get/{key}`: Recupera dados armazenados no cache utilizando uma chave.

### 4. **Autenticação e Registro de Usuários**
- Rota `POST /auth/register`: Registra um novo usuário no sistema.
- Rota `POST /auth/login`: Realiza login do usuário e retorna um token JWT para autenticação.

## Funcionalidades a Serem Implementadas

- **Filas (Celery + Redis)**: Implementação de processamento assíncrono de tarefas, como o envio de notificações ou o processamento de grandes volumes de dados.
- **Agregação de Dados mais Complexa**: Melhorias nas consultas agregadas, incluindo mais filtros e métricas.
- **Monitoramento e Logs**: Implementação de monitoramento e geração de logs para melhorar a visibilidade da API.

## Documentação da API

A API está completamente documentada e pode ser acessada através do Swagger UI integrado ao FastAPI.

1. **Swagger**: Acesse a documentação da API em `http://localhost:8000/docs` após rodar o projeto. Lá você encontrará todas as rotas disponíveis e poderá testar as funcionalidades diretamente.

2. **Redoc**: Também está disponível uma documentação alternativa em `http://localhost:8000/redoc`.

## Como Rodar o Projeto

### 1. **Clone o Repositório**

```bash
git clone https://github.com/seuusuario/exame-backend-dt-labs-2025.git
cd exame-backend-dt-labs-2025
```

### 2. **Configuração do `.env`**

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis de ambiente:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
```

### 3. **Rodando com Docker Compose**

Este projeto está configurado para ser executado com **Docker Compose**, que irá iniciar os contêineres necessários para a API, PostgreSQL e Redis.

#### a. **Construindo e Iniciando os Contêineres**

No diretório raiz do projeto, execute:

```bash
docker-compose up --build
```

Este comando irá:
- Construir a imagem do Docker para a API.
- Iniciar o contêiner para a API, banco de dados PostgreSQL e Redis.

#### b. **Acessando a API**

Após a construção dos contêineres, a API estará disponível em:

- **Swagger**: `http://localhost:8000/docs`
- **Redoc**: `http://localhost:8000/redoc`

#### c. **Parando os Contêineres**

Para parar os contêineres, execute:

```bash
docker-compose down
```

## Docker Compose Configuration

Aqui está o `docker-compose.yml` para rodar o projeto com PostgreSQL, Redis e a API:

```yaml
version: '3.7'

services:
  app:
    image: python:3.9-slim
    container_name: fastapi_app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/app
    working_dir: /app
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    networks:
      - backend

  db:
    image: postgres:13
    container_name: postgres_db
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: dbname
    ports:
      - "5432:5432"
    networks:
      - backend
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    container_name: redis_cache
    ports:
      - "6379:6379"
    networks:
      - backend

networks:
  backend:
    driver: bridge

volumes:
  postgres_data:
```

### Explicação do `docker-compose.yml`:
- **app**: Contêiner para a API, que executa o FastAPI com Uvicorn.
- **db**: Contêiner para o PostgreSQL, com configuração de usuário, senha e banco de dados.
- **redis**: Contêiner para o Redis, usado como cache.
- **volumes**: Volume persistente para os dados do PostgreSQL.

### 4. **Executando os Testes**

Você pode rodar os testes de unidade utilizando o `pytest`. Para rodar os testes, basta executar o seguinte comando:

```bash
pytest
```

## Contribuindo

Se você quiser contribuir para o projeto, fique à vontade para fazer um fork, criar uma branch e submeter um pull request.

