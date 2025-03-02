from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Server
from app.schemas import ServerCreate, ServerResponse
from app.utils.security import get_current_user
import ulid

router = APIRouter(prefix="/servers", tags=["Servers"])

@router.post("/", response_model=ServerResponse, status_code=status.HTTP_201_CREATED,
                  summary="Register a new server", 
                  description="Registers a new server in the system. Ensures the server name is unique and generates a ULID.")


async def register_server(server_data: ServerCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    print(f"🔍 DEBUG - Criando servidor para usuário {user.id}")
    
    # Check if a server with the same name already exists
    existing_server = db.query(Server).filter(Server.name == server_data.name).first()
    if existing_server:
        raise HTTPException(status_code=400, detail="Server with this name already exists")

   # Gera um ULID para o novo servidor
    new_server = Server(
        ulid=str(ulid.new()),
        name=server_data.name,
        user_id=user.id  # 🔹 Associamos o servidor ao usuário autenticado
    )

    db.add(new_server)
    db.commit()
    db.refresh(new_server)

    print(f"✅ DEBUG - Servidor criado: {new_server.ulid}, Usuário: {user.id}")

    return new_server
