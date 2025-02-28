from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Server
from app.schemas import ServerCreate, ServerResponse
from app.utils.security import get_current_user
import ulid

router = APIRouter(prefix="/servers", tags=["Servers"])

@router.post("/", response_model=ServerResponse)
def register_server(server_data: ServerCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Verifica se já existe um servidor com esse nome
    existing_server = db.query(Server).filter(Server.name == server_data.name).first()
    if existing_server:
        raise HTTPException(status_code=400, detail="Server with this name already exists")

    # Gera um ULID para o servidor
    server_ulid = str(ulid.new())

    # Cria o novo servidor
    new_server = Server(ulid=server_ulid, name=server_data.name)
    db.add(new_server)
    db.commit()
    db.refresh(new_server)

    return new_server
