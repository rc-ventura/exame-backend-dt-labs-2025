from fastapi import FastAPI
from app.routes import auth, servers ,sensor_data, health
from app.database import engine, Base, init_db
from app.routes import cache


app = FastAPI()

init_db()

# Incluir as rotas
app.include_router(auth.router)
app.include_router(sensor_data.router)
app.include_router(servers.router)
app.include_router(health.router)
app.include_router(cache.router)



@app.get("/")
def root():
    return {"message": "API is running"}
