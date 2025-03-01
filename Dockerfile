# Escolher a imagem base com Python 3.13
FROM python:3.13-slim

# Definir o diretório de trabalho no contêiner
WORKDIR /app

# Copiar o arquivo requirements.txt para dentro do contêiner
COPY requirements.txt .

# Instalar as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos os arquivos do projeto para dentro do contêiner
COPY . .

# Expor a porta que o FastAPI vai rodar
EXPOSE 8000

# Definir o comando para rodar a aplicação com o Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
