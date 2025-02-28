from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Server, SensorData
from app.schemas import ServerHealthResponse
from typing import List, Optional 
from app.utils.security import get_current_user

OFFLINE_THRESHOLD = timedelta(seconds=10)  # Exemplo de 10 segundos para considerar offline

router = APIRouter(prefix="/health", tags=["Server Health"])

@router.get("/all", response_model=List[ServerHealthResponse])
def get_all_servers_health(db: Session = Depends(get_db), user = Depends(get_current_user)):
    """
    Retorna o status de todos os servidores cadastrados daquele usuário.
    - Requer autenticação JWT.
    """

    # Verifica se o usuário está autenticado
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Obtém todos os servidores cadastrados
    servers = db.query(Server).all()
    
    if not servers:
        raise HTTPException(status_code=404, detail="No servers found for this user")

    now = datetime.utcnow()
    health_statuses = []

    for server in servers:
        last_data = (
            db.query(SensorData)
            .filter(SensorData.server_ulid == server.ulid)
            .order_by(SensorData.timestamp.desc())
            .first()
        )

        # Verificação do status baseado na última leitura de sensor
        if not last_data:
            status = "offline"
        elif now - last_data.timestamp > OFFLINE_THRESHOLD:
            status = "offline"
        else:
            status = "online"

        health_statuses.append(ServerHealthResponse(
            server_ulid=server.ulid,
            status=status,
            server_name=server.name
        ))

    return health_statuses
