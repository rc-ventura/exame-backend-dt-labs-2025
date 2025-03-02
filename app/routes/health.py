from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from app.database import get_db
from app.models import Server, SensorData
from app.schemas import ServerHealthResponse
from app.utils.security import get_current_user
from app.utils.cache import get_cache_key, set_cache_key
import json  # Import necessário para manipulação do cache

OFFLINE_THRESHOLD = timedelta(seconds=10)
CACHE_EXPIRATION = timedelta(minutes=5)

router = APIRouter(prefix="/health", tags=["Server Health"])

@router.get("/all", response_model=List[ServerHealthResponse])
async def get_all_servers_health(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Retorna o status de todos os servidores pertencentes ao usuário autenticado.
    - Requer autenticação JWT.
    """

    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    print(f"🔍 DEBUG - Buscando servidores do usuário {user.id}")

    # Tenta obter os dados do cache primeiro
    cache_key = f"user_servers_health_status:{user.id}"
    cached_data = await get_cache_key(cache_key)

    if cached_data:
        try:
            cached_list = json.loads(cached_data)  # Convertendo JSON para lista de dicionários
            print(f"✅ DEBUG - Dados do cache recuperados para {user.id}: {cached_list}")
            return [ServerHealthResponse.parse_obj(item) for item in cached_list]
        except Exception:
            print(f"⚠️ WARNING - Cache inválido: {cached_data}")

    # 🔹 Obtém apenas os servidores do usuário autenticado
    servers = db.query(Server).filter(Server.user_id == user.id).all()

    print(f"🔍 DEBUG - Servidores encontrados: {len(servers)}")

    if not servers:
        print("⚠️ WARNING - Usuário não possui servidores cadastrados.")
        return []  # Retorna lista vazia ao invés de erro 404

    now = datetime.utcnow()
    health_statuses = []

    for server in servers:
        print(f"🖥️ Servidor encontrado -> ULID: {server.ulid}, Nome: {server.name}")

        last_data = (
            db.query(SensorData)
            .filter(SensorData.server_ulid == server.ulid)
            .order_by(SensorData.timestamp.desc())
            .first()
        )

        status = "online" if not last_data or now - last_data.timestamp <= OFFLINE_THRESHOLD else "offline"

        health_statuses.append(ServerHealthResponse(
            server_ulid=server.ulid,
            status=status,
            server_name=server.name
        ))

    print("✅ DEBUG - Todos os servidores processados com sucesso!")

    # 🔹 Salvando no cache corretamente como JSON
    health_statuses_dict = [item.dict() for item in health_statuses]
    await set_cache_key(cache_key, json.dumps(health_statuses_dict), expire=int(CACHE_EXPIRATION.total_seconds()))

    return health_statuses



@router.get("/{server_ulid}", response_model=ServerHealthResponse)
async def get_server_health_by_id(server_ulid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Retorna o status de um servidor específico pelo ULID.
    - Requer autenticação JWT.
    """
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    cache_key = f"server_health_status:{server_ulid}"
    cached_data = await get_cache_key(cache_key)

    if cached_data:
        try:
            cached_obj = ServerHealthResponse(**json.loads(cached_data))  # Convertendo JSON -> Pydantic
            return cached_obj
        except Exception:
            print(f"WARNING - Cache inválido: {cached_data}")  # Log apenas se der erro

    server = db.query(Server).filter(Server.ulid == server_ulid).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    last_data = (
        db.query(SensorData)
        .filter(SensorData.server_ulid == server.ulid)
        .order_by(SensorData.timestamp.desc())
        .first()
    )

    now = datetime.utcnow()
    status = "online" if not last_data or now - last_data.timestamp <= OFFLINE_THRESHOLD else "offline"

    try:
        server_health = ServerHealthResponse(
            server_ulid=server.ulid,
            status=status,
            server_name=server.name
        )
        print(f"DEBUG - Server Health Response: {server_health.dict()}")

        # Salvando no cache como JSON
        await set_cache_key(cache_key, json.dumps(server_health.dict()), expire=int(CACHE_EXPIRATION.total_seconds()))
        return server_health
    except Exception as e:
        print(f"ERROR - Failed to serialize response: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
