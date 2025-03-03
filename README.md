# exame-backend-dt-labs-2025

## Projeto: API de Sensores com Usuários, Cache e Banco de Dados

Este projeto é uma **API RESTful** construída com **FastAPI** para gerenciar dados de sensores, associando-os a servidores e usuários autenticados. Utilizamos **PostgreSQL** como banco de dados, **Redis** para cache e **Docker** para facilitar a configuração e execução dos serviços.

---

## 🚀 **Tecnologias Utilizadas**

- **FastAPI**: Framework moderno para criação de APIs assíncronas em Python.
- **PostgreSQL**: Banco de dados relacional para armazenar servidores, usuários e dados de sensores.
- **Redis**: Armazenamento em memória para cache de dados, melhorando a performance das consultas.
- **Docker & Docker Compose**: Facilita a implantação da API e dos serviços auxiliares.
- **SQLAlchemy**: ORM utilizado para interagir com o PostgreSQL.
- **Pydantic**: Biblioteca para validação de dados com modelos estruturados.
- **pytest**: Framework para criação de testes automatizados.

---

## ✅ **Funcionalidades Implementadas**

### 🔹 **1. Gerenciamento de Servidores**

- **Rota `POST /servers/`** → Criação de servidores associados ao usuário autenticado.
- **Rota `GET /servers/{server_ulid}`** → Retorna detalhes de um servidor específico.
- **Rota `GET /servers/all`** → Lista todos os servidores do usuário autenticado.

### 🔹 **2. Gerenciamento de Saúde dos Servidores**

- **Rota `GET /health/{server_ulid}`** → Retorna o status de um servidor específico.
- **Rota `GET /health/all`** → Retorna o status de todos os servidores pertencentes ao usuário autenticado.

### 🔹 **3. Cadastro e Consulta de Dados de Sensores**

- **Rota `POST /data/`** → Cadastra dados de sensores associados a um servidor.
- **Rota `GET /data/`** → Retorna os dados de sensores com filtros opcionais (servidor e período).
- **Rota `GET /data?aggregation={level}`** → Agregação de dados de sensores (por minuto, hora ou dia).

### 🔹 **4. Cache com Redis**

- **Rota `POST /cache/set`** → Armazena dados no cache do Redis.
- **Rota `GET /cache/get/{key}`** → Recupera dados do cache do Redis.

### 🔹 **5. Autenticação e Gerenciamento de Usuários**

- **Rota `POST /auth/register`** → Registra um novo usuário.
- **Rota `POST /auth/login`** → Gera um token JWT para autenticação.
- **JWT Token** → Protege as rotas e identifica automaticamente o usuário autenticado.

---

## 🔧 **Funcionalidades a Serem Implementadas**

- **Filas com Celery + Redis** → Para tarefas assíncronas, como notificações e cálculos pesados.
- **Melhoria nas Consultas de Dados** → Mais filtros e métricas avançadas.
- **Monitoramento & Logging** → Integração com ferramentas de monitoramento e geração de logs.
- **Criação de um Frontend** → Desenvolver uma interface gráfica para interação com a API.

---

## 📄 **Documentação da API**

A API está documentada automaticamente pelo **FastAPI**:

- **Swagger UI** → Acesse `http://localhost:8000/docs`
- **ReDoc** → Acesse `http://localhost:8000/redoc`

Aqui você pode testar as rotas diretamente e visualizar os modelos de entrada e saída.

---

## ▶️ **Como Rodar o Projeto**

### **1️⃣ Clonar o Repositório**

```bash
git clone https://github.com/seuusuario/exame-backend-dt-labs-2025.git
cd exame-backend-dt-labs-2025
```

### **2️⃣ Configurar as Variáveis de Ambiente (`.env`)**

Para rodar o projeto, é necessário configurar as variáveis de ambiente. Crie um arquivo `.env` na raiz do projeto e defina as seguintes variáveis:

```env
SECRET_KEY=your_secret_key
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name
DATABASE_URL=postgresql://your_postgres_user:your_postgres_password@db:5432/your_database_name
REDIS_URL=redis://redis:6379
```

> **Importante:** Ajuste os valores conforme necessário. A `SECRET_KEY` é essencial para a autenticação JWT e deve ser mantida segura.

### **3️⃣ Rodar o Projeto com Docker Compose**

Execute o seguinte comando para subir os serviços:

```bash
docker-compose up --build
```

Isso irá iniciar os seguintes serviços:

- **FastAPI** rodando na porta `8000`
- **PostgreSQL** rodando na porta `5432`
- **Redis** rodando na porta `6379`

Após iniciado, a API estará disponível em:

- **Swagger UI** → `http://localhost:8000/docs`
- **ReDoc** → `http://localhost:8000/redoc`

### **4️⃣ Parar os Contêineres**

```bash
docker-compose down
```

---

## ✅ **Executando os Testes**

Os testes cobrem as seguintes funcionalidades:
- Cadastro e login de usuários.
- Criação e consulta de servidores.
- Inserção e recuperação de dados de sensores.
- Validação do cache com Redis.
- Autenticação via JWT.

Para rodar os testes, primeiro entre no container do FastAPI:

```bash
docker exec -it fastapi_app bash
```

Dentro do container, execute os testes com:

```bash
pytest
```

Se quiser um relatório detalhado, use:

```bash
pytest -v
```

Para sair do container, utilize:

```bash
exit
```

Caso prefira rodar os testes sem entrar no container, utilize:

```bash
docker exec -it fastapi_app pytest
```

Isso executará os testes automatizados para validar a API.

---

## 🤝 **Contribuindo**

Se você deseja contribuir com o projeto, siga os passos abaixo:

1. Faça um **fork** do repositório.
2. Crie uma **branch** para suas alterações: `git checkout -b minha-feature`
3. Faça commit das alterações: `git commit -m 'Adicionando nova funcionalidade'`
4. Faça **push** para sua branch: `git push origin minha-feature`
5. Abra um **Pull Request** para revisão.

---

## 🔥 **Conclusão**

Este projeto fornece uma API robusta para gerenciamento de sensores e servidores, utilizando autenticação JWT, cache com Redis e persistência de dados com PostgreSQL. 🚀

Agora com suporte a **usuários autenticados**, cada servidor pertence ao seu respectivo dono, garantindo segurança e melhor organização dos dados. 💡

**Falta a criação de um frontend para facilitar a interação com a API.**

Para dúvidas ou sugestões, abra uma **issue** no GitHub!

---

🎯 **Autor:** Rafael Ventura  
🔗 **Repositório:** [GitHub](https://github.com/rc-ventura/exame-backend-dt-labs-2025)

