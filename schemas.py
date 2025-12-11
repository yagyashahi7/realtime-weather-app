from pydantic import BaseModel
from datetime import date
from typing import Optional

class WeatherRequest(BaseModel):
    location: str  # e.g., "New York", "10001", "40.7128,-74.0060", "Eiffel Tower"
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None

class WeatherUpdate(BaseModel):
    location: Optional[str] = None
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    temperature: Optional[float] = None
    weather_description: Optional[str] = None

class WeatherResponse(BaseModel):
    id: int
    location: str
    date_range_start: Optional[date]
    date_range_end: Optional[date]
    temperature: float
    weather_description: str

    class Config:
        from_attributes = True