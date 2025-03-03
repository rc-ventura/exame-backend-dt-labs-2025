# Usar a imagem oficial do Python
FROM python:3.9-slim

# Instalar dependências do sistema necessárias para a compilação
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libc-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar um diretório de trabalho dentro do container
WORKDIR /app

# Copiar o arquivo de dependências do projeto para o container
COPY requirements.txt .

# Instalar as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código do projeto para o container
COPY . .

# Expor a porta onde o FastAPI estará rodando
EXPOSE 8000

# Comando para rodar o FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
