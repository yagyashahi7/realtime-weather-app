from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import services.weather_service as weather_service
from schemas import WeatherRequest, WeatherUpdate, WeatherResponse
from db import get_db

router = APIRouter()

@router.post("/", response_model=WeatherResponse)
async def create_weather(request: WeatherRequest, db: Session = Depends(get_db)):
    return await weather_service.create_weather_record(request, db)

@router.get("/", response_model=List[WeatherResponse])
async def read_weathers(db: Session = Depends(get_db)):
    return weather_service.get_weathers(db)

@router.get("/{weather_id}", response_model=WeatherResponse)
async def read_weather(weather_id: int, db: Session = Depends(get_db)):
    return weather_service.get_weather(weather_id, db)

@router.put("/{weather_id}", response_model=WeatherResponse)
async def update_weather(weather_id: int, update: WeatherUpdate, db: Session = Depends(get_db)):
    return await weather_service.update_weather(weather_id, update, db)

@router.delete("/{weather_id}")
async def delete_weather(weather_id: int, db: Session = Depends(get_db)):
    return weather_service.delete_weather(weather_id, db)

@router.get("/export/{format}")
async def export_data(format: str, db: Session = Depends(get_db)):
    if format not in ["json", "csv", "pdf", "xml", "markdown"]:
        raise HTTPException(status_code=400, detail="Unsupported format")
    return weather_service.export_data(format, db)