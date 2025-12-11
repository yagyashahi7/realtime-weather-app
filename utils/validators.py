from datetime import date, timedelta
from weather_api import check_location_exists  # Reuse API to validate location
from fastapi import HTTPException

def validate_date_range(start: date | None, end: date | None):
    if start and end:
        if start > end:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
        if (end - start) > timedelta(days=7):
            raise HTTPException(status_code=400, detail="Forecast range cannot exceed 7 days.")
        # No future-only check; Open-Meteo supports historical
    # Additional checks

async def validate_location(location: str) -> bool:
    return await check_location_exists(location)  # Fuzzy match via API response
