from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database import get_db
from app.models import SensorData, Server
from app.schemas import SensorDataResponse, SensorDataCreate
import ulid
from typing import List, Optional, Union
from app.utils.cache import set_cache_key, get_cache_key

router = APIRouter(prefix="/data", tags=["Sensor Data"])

# Função para criar o timestamp no formato ISO 8601
def generate_iso_timestamp():
    return datetime.utcnow().isoformat()

@router.post("/", response_model=SensorDataResponse, status_code=status.HTTP_201_CREATED)
async def register_sensor_data(data: SensorDataCreate, db: Session = Depends(get_db)):
    """
    Registra uma nova leitura de sensores de um servidor no banco de dados.
        E, automaticamente, armazena os dados no cache Redis.

    """

    # Verifica se o servidor existe
    server = db.query(Server).filter(Server.ulid == data.server_ulid).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # Verifica se já existe um registro com o mesmo servidor e timestamp
    existing_data = db.query(SensorData).filter(
        SensorData.server_ulid == data.server_ulid,
        SensorData.timestamp == generate_iso_timestamp()
    ).first()

    if existing_data:
        raise HTTPException(status_code=400, detail="Duplicate data entry for the same timestamp.")

    # Cria um novo registro de leitura dos sensores
    sensor_data = SensorData(
        id=str(ulid.new()),
        server_ulid=data.server_ulid,
        timestamp=datetime.utcnow(),  # Passa o timestamp atual para o banco de dados
        temperature=data.temperature,
        humidity=data.humidity,
        voltage=data.voltage,
        current=data.current
    )

    db.add(sensor_data)
    db.commit()
    db.refresh(sensor_data)

    # Armazena os dados no cache Redis após a inserção no banco de dados
    await set_cache_key(sensor_data.id, str(sensor_data.__dict__))  


    return SensorDataResponse.from_orm(sensor_data)

@router.get("/", response_model=Union[List[SensorDataResponse], List[SensorDataResponse]])
async def get_sensor_data(
    server_ulid: Optional[str] = Query(None, description="Filter by server ULID"),
    start_time: Optional[datetime] = Query(None, description="Start time for filtering"),
    end_time: Optional[datetime] = Query(None, description="End time for filtering"),
    aggregation: Optional[str] = Query(None, description="Aggregation level: minute, hour, day. Default is no aggregation."),
    db: Session = Depends(get_db)
):
    """
    Obtém os dados dos sensores, podendo ser filtrado por servidor e intervalo de tempo.
    Se a agregação for informada, calcula a média dos valores dentro do intervalo especificado.

    Esta rota também verifica o cache Redis para os dados.


    Parâmetros:
    - aggregation: Opcional. Define a granularidade da agregação de dados. Valores possíveis: "minute", "hour", "day".
    """

     # Verificação de cache
    cache_key = f"sensor_data:{server_ulid}:{start_time}:{end_time}:{aggregation}"  # Gerar chave para cache
    cached_data = await get_cache_key(cache_key)

    if cached_data:
        # Caso os dados estejam no cache, retornamos imediatamente
        return cached_data

    # Caso os dados não estejam no cache, vamos acessar o banco de dados
    query = db.query(SensorData)


    # Filtra por servidor, se informado
    if server_ulid:
        query = query.filter(SensorData.server_ulid == server_ulid)

    # Filtra por intervalo de tempo, se informado
    if start_time and end_time:
        query = query.filter(SensorData.timestamp.between(start_time, end_time))

    if aggregation:
        if aggregation not in ["minute", "hour", "day"]:
            raise HTTPException(status_code=400, detail="Invalid aggregation type. Use 'minute', 'hour', or 'day'.")

        # Define o agrupamento de acordo com o tipo de agregação
        time_format = {
            "minute": func.date_trunc("minute", SensorData.timestamp),
            "hour": func.date_trunc("hour", SensorData.timestamp),
            "day": func.date_trunc("day", SensorData.timestamp)
        }[aggregation]

        # Agrega os dados por timestamp truncado (minute, hour, day) e calcula a média
        query = (
            query.with_entities(
                SensorData.server_ulid,
                time_format.label("timestamp"),
                func.avg(SensorData.temperature).label("average_temperature"),
                func.avg(SensorData.humidity).label("average_humidity"),
                func.avg(SensorData.voltage).label("average_voltage"),
                func.avg(SensorData.current).label("average_current"),
            )
            .group_by(SensorData.server_ulid, time_format)  # Adiciona server_ulid ao GROUP BY
            .order_by(time_format)
        )

        aggregated_data = query.all()

        if not aggregated_data:
            raise HTTPException(status_code=404, detail="No sensor data found")

        # Retorna os dados agregados
        return [
            SensorDataResponse(
                id=str(ulid.new()),  # Gerar um novo id para dados agregados
                server_ulid=data.server_ulid,
                timestamp=data.timestamp.isoformat(),
                temperature=data.average_temperature,
                humidity=data.average_humidity,
                voltage=data.average_voltage,
                current=data.average_current
            )
            for data in aggregated_data
        ]
    
    # Caso não seja solicitado agregação, retorna os dados originais
    sensor_data = query.all()

    if not sensor_data:
        raise HTTPException(status_code=404, detail="No sensor data found")

    return [
        SensorDataResponse(
            id=str(data.id),
            server_ulid=data.server_ulid,
            timestamp=data.timestamp.isoformat(),
            temperature=data.temperature,
            humidity=data.humidity,
            voltage=data.voltage,
            current=data.current
        )
        for data in sensor_data
    ]
