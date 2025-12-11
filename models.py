from sqlalchemy import Column, Integer, String, Float, Date
from db import Base

class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True)
    date_range_start = Column(Date)
    date_range_end = Column(Date)
    temperature = Column(Float)  # Average or current temp
    weather_description = Column(String)
    # Add more fields as needed, e.g., precipitation, etc.