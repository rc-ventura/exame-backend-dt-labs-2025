from sqlalchemy import create_engine, text
import os

# Pegue a URL do banco de dados do .env ou use um valor padrão
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/meu_banco")

try:
    # Criar a engine de conexão com o banco
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).fetchone()
        print(f"✅ Conexão com o banco de dados bem-sucedida! Resultado: {result[0]}")
except Exception as e:
    print(f"❌ Erro ao conectar ao banco de dados: {e}")
