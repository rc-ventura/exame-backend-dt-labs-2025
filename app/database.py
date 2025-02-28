# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

# Pegar URL do banco
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"📌 DATABASE_URL carregada: {DATABASE_URL}")

# Criar conexão com o banco
engine = create_engine(DATABASE_URL)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar base para os modelos
Base = declarative_base()

# 🚀 Adicione essa linha para criar tabelas automaticamente
def init_db():
    Base.metadata.create_all(bind=engine)

# 🚀 Função para obter conexão com o banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()