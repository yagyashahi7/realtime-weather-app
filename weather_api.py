import os
import aiohttp
from dotenv import load_dotenv
from datetime import date, datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # Optional

async def geocode_location(location: str) -> dict:
    async with aiohttp.ClientSession() as session:
        url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
        headers = {'User-Agent': 'WeatherApp/1.0'}  # Required for Nominatim
        async with session.get(url, headers=headers) as response:
            logging.info(f"Geocode API status for {location}: {response.status}")
            if response.status != 200:
                error_data = await response.text()
                logging.error(f"Geocode API error: {error_data}")
                raise ValueError(f"Failed to geocode location: {error_data}")
            data = await response.json()
            if not data:
                raise ValueError("Location not found")
            return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}

async def fetch_current_weather(location: str) -> dict:
    async with aiohttp.ClientSession() as session:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
        async with session.get(url) as response:
            logging.info(f"Current weather API status for {location}: {response.status}")
            if response.status != 200:
                error_data = await response.text()
                logging.error(f"Current weather API error: {error_data}")
                raise ValueError(f"Failed to fetch weather: {error_data}")
            data = await response.json()
            return {"temperature": data["main"]["temp"], "description": data["weather"][0]["description"]}

async def fetch_forecast(location: str, start: date, end: date) -> dict:
    geo = await geocode_location(location)
    lat, lon = geo["lat"], geo["lon"]
    async with aiohttp.ClientSession() as session:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_mean,weather_code&start_date={start}&end_date={end}&timezone=UTC"
        async with session.get(url) as response:
            logging.info(f"Forecast API status for {location} ({start} to {end}): {response.status}")
            if response.status != 200:
                error_data = await response.text()
                logging.error(f"Forecast API error: {error_data}")
                raise ValueError(f"Failed to fetch forecast: {error_data}")
            data = await response.json()
            temps = data["daily"]["temperature_2m_mean"]
            if not temps:
                raise ValueError("No forecast data available for the date range. Open-Meteo supports historical since 1940 and future up to 7 days.")
            avg_temp = sum(temps) / len(temps)
            desc_code = data["daily"]["weather_code"][0] if data["daily"]["weather_code"] else 0
            desc_map = {0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast", 45: "fog", 51: "light drizzle", 61: "light rain", 80: "rain showers"}  # Simplified WMO codes
            desc = desc_map.get(desc_code, "unknown")
            return {"temperature": avg_temp, "description": f"Forecast average: {desc}"}

async def check_location_exists(location: str) -> bool:
    try:
        await fetch_current_weather(location)
        return True
    except ValueError as e:
        logging.error(f"Location validation failed for {location}: {str(e)}")
        return False

# Optional: YouTube integration
async def fetch_youtube_videos(location: str) -> list:
    if not YOUTUBE_API_KEY:
        return []
    async with aiohttp.ClientSession() as session:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={location}+travel&key={YOUTUBE_API_KEY}"
        async with session.get(url) as response:
            data = await response.json()
            return [item["snippet"]["title"] for item in data.get("items", [])]




# import os
# import aiohttp
# from dotenv import load_dotenv
# from datetime import date, datetime, timezone

# load_dotenv()

# OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
# YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # Optional

# async def fetch_current_weather(location: str) -> dict:
#     async with aiohttp.ClientSession() as session:
#         url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
#         async with session.get(url) as response:
#             if response.status != 200:
#                 raise ValueError("Failed to fetch weather")
#             data = await response.json()
#             return {"temperature": data["main"]["temp"], "description": data["weather"][0]["description"]}

# async def fetch_forecast(location: str, start: date, end: date) -> dict:
#     async with aiohttp.ClientSession() as session:
#         url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
#         async with session.get(url) as response:
#             if response.status != 200:
#                 raise ValueError("Failed to fetch forecast")
#             data = await response.json()
#             start_ts = int(datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc).timestamp())
#             end_ts = int(datetime.combine(end, datetime.max.time(), tzinfo=timezone.utc).timestamp())
#             filtered_temps = [item["main"]["temp"] for item in data["list"] if start_ts <= item["dt"] <= end_ts]
#             desc = data["list"][0]["weather"][0]["description"] if data["list"] else "No data"
#             avg_temp = sum(filtered_temps) / len(filtered_temps) if filtered_temps else 0
#             return {"temperature": avg_temp, "description": f"Forecast average: {desc}"}

# async def check_location_exists(location: str) -> bool:
#     try:
#         await fetch_current_weather(location)
#         return True
#     except ValueError:
#         return False

# # Optional: YouTube integration
# async def fetch_youtube_videos(location: str) -> list:
#     if not YOUTUBE_API_KEY:
#         return []
#     async with aiohttp.ClientSession() as session:
#         url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={location}+travel&key={YOUTUBE_API_KEY}"
#         async with session.get(url) as response:
#             data = await response.json()
#             return [item["snippet"]["title"] for item in data.get("items", [])]