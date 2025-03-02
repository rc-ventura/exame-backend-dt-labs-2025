from fastapi import APIRouter, HTTPException, status
from app.utils.cache import set_cache_key, get_cache_key

router = APIRouter(prefix="/cache", tags=["Cache"])

@router.post("/set", status_code=status.HTTP_200_OK)
async def set_cache_data(key: str, value: str):
    """
    Armazena dados no Redis (cache).
    - key: Chave para armazenar os dados
    - value: Valor a ser armazenado
    """
    try:
        await set_cache_key(key, value)
        return {"message": "Data cached successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get/{key}", status_code=status.HTTP_200_OK)
async def get_cache_data(key: str):
    """
    Recupera dados armazenados no Redis (cache).
    - key: Chave do dado armazenado no Redis
    """
    cached_value = await get_cache_key(key)
    if cached_value:
        return {"key": key, "value": cached_value}
    else:
        raise HTTPException(status_code=404, detail="Cache not found")
