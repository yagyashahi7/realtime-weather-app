from sqlalchemy.orm import Session
from models import WeatherRecord
from schemas import WeatherRequest, WeatherUpdate, WeatherResponse
from utils.validators import validate_date_range, validate_location
from weather_api import fetch_current_weather, fetch_forecast
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import json
import csv
from io import StringIO, BytesIO
from typing import List
from fpdf import FPDF
import xml.etree.ElementTree as ET
from datetime import datetime

async def create_weather_record(request: WeatherRequest, db: Session):
    validate_date_range(request.date_range_start, request.date_range_end)
    if not await validate_location(request.location):
        raise HTTPException(status_code=400, detail="Invalid location")

    try:
        if request.date_range_start and request.date_range_end:
            weather_data = await fetch_forecast(request.location, request.date_range_start, request.date_range_end)
        else:
            weather_data = await fetch_current_weather(request.location)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    record = WeatherRecord(
        location=request.location,
        date_range_start=request.date_range_start,
        date_range_end=request.date_range_end,
        temperature=weather_data["temperature"],
        weather_description=weather_data["description"]
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return WeatherResponse.model_validate(record)

def get_weathers(db: Session) -> List[WeatherResponse]:
    records = db.query(WeatherRecord).all()
    return [WeatherResponse.model_validate(r) for r in records]

def get_weather(weather_id: int, db: Session) -> WeatherResponse:
    record = db.query(WeatherRecord).filter(WeatherRecord.id == weather_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return WeatherResponse.model_validate(record)

async def update_weather(weather_id: int, update: WeatherUpdate, db: Session) -> WeatherResponse:
    record = db.query(WeatherRecord).filter(WeatherRecord.id == weather_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    dates_changed = update.date_range_start or update.date_range_end
    if update.location:
        if not await validate_location(update.location):
            raise HTTPException(status_code=400, detail="Invalid location")
        record.location = update.location
    if dates_changed:
        new_start = update.date_range_start or record.date_range_start
        new_end = update.date_range_end or record.date_range_end
        validate_date_range(new_start, new_end)
        record.date_range_start = new_start
        record.date_range_end = new_end
        # Re-fetch weather
        if new_start and new_end:
            weather_data = await fetch_forecast(record.location, new_start, new_end)
        else:
            weather_data = await fetch_current_weather(record.location)
        record.temperature = weather_data["temperature"]
        record.weather_description = weather_data["description"]
    if update.temperature:
        record.temperature = update.temperature
    if update.weather_description:
        record.weather_description = update.weather_description
    db.commit()
    db.refresh(record)
    return WeatherResponse.model_validate(record)

def delete_weather(weather_id: int, db: Session):
    record = db.query(WeatherRecord).filter(WeatherRecord.id == weather_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"detail": "Record deleted"}

def export_data(format: str, db: Session):
    records = get_weathers(db)
    clean_records = [r.model_dump() for r in records]
    if format == "json":
        return json.dumps(clean_records, default=str, indent=2)
    elif format == "csv":
        output = StringIO()
        writer = csv.writer(output)
        if clean_records:
            writer.writerow(clean_records[0].keys())
            for r in clean_records:
                writer.writerow(r.values())
        return output.getvalue()
    elif format == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        headers = ["ID", "Location", "Start Date", "End Date", "Temperature", "Description"]
        pdf.cell(200, 10, txt="Weather Records", ln=1, align="C")
        for header in headers:
            pdf.cell(30, 10, header, 1)
        pdf.ln()
        for r in clean_records:
            pdf.cell(30, 10, str(r["id"]), 1)
            pdf.cell(30, 10, r["location"], 1)
            pdf.cell(30, 10, str(r["date_range_start"]), 1)
            pdf.cell(30, 10, str(r["date_range_end"]), 1)
            pdf.cell(30, 10, str(r["temperature"]), 1)
            pdf.cell(30, 10, r["weather_description"], 1)
            pdf.ln()
        bio = BytesIO()
        bio.write(pdf.output(dest='S').encode('latin1'))
        bio.seek(0)
        return StreamingResponse(bio, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=weather_records.pdf"})
    elif format == "xml":
        root = ET.Element("weather_records")
        for r in clean_records:
            record_elem = ET.SubElement(root, "record")
            for k, v in r.items():
                child = ET.SubElement(record_elem, k)
                child.text = str(v)
        xml_str = ET.tostring(root, encoding='unicode', method='xml')
        return xml_str
    elif format == "markdown":
        if not clean_records:
            return "No records found."
        headers = list(clean_records[0].keys())
        md = "| " + " | ".join(headers) + " |\n"
        md += "| " + "--- | " * len(headers) + "\n"
        for r in clean_records:
            md += "| " + " | ".join(str(v) for v in r.values()) + " |\n"
        return md





# from sqlalchemy.orm import Session
# from models import WeatherRecord
# from schemas import WeatherRequest, WeatherUpdate, WeatherResponse
# from utils.validators import validate_date_range, validate_location
# from weather_api import fetch_current_weather, fetch_forecast
# from fastapi import HTTPException
# from fastapi.responses import StreamingResponse
# import json
# import csv
# from io import StringIO, BytesIO
# from typing import List
# from fpdf import FPDF
# import xml.etree.ElementTree as ET
# from datetime import datetime

# async def create_weather_record(request: WeatherRequest, db: Session):
#     validate_date_range(request.date_range_start, request.date_range_end)
#     if not await validate_location(request.location):
#         raise HTTPException(status_code=400, detail="Invalid location")

#     if request.date_range_start and request.date_range_end:
#         weather_data = await fetch_forecast(request.location, request.date_range_start, request.date_range_end)
#     else:
#         weather_data = await fetch_current_weather(request.location)

#     record = WeatherRecord(
#         location=request.location,
#         date_range_start=request.date_range_start,
#         date_range_end=request.date_range_end,
#         temperature=weather_data["temperature"],
#         weather_description=weather_data["description"]
#     )
#     db.add(record)
#     db.commit()
#     db.refresh(record)
#     return WeatherResponse.model_validate(record)

# def get_weathers(db: Session) -> List[WeatherResponse]:
#     records = db.query(WeatherRecord).all()
#     return [WeatherResponse.model_validate(r) for r in records]

# def get_weather(weather_id: int, db: Session) -> WeatherResponse:
#     record = db.query(WeatherRecord).filter(WeatherRecord.id == weather_id).first()
#     if not record:
#         raise HTTPException(status_code=404, detail="Record not found")
#     return WeatherResponse.model_validate(record)

# async def update_weather(weather_id: int, update: WeatherUpdate, db: Session) -> WeatherResponse:
#     record = db.query(WeatherRecord).filter(WeatherRecord.id == weather_id).first()
#     if not record:
#         raise HTTPException(status_code=404, detail="Record not found")
#     dates_changed = update.date_range_start or update.date_range_end
#     if update.location:
#         if not await validate_location(update.location):
#             raise HTTPException(status_code=400, detail="Invalid location")
#         record.location = update.location
#     if dates_changed:
#         new_start = update.date_range_start or record.date_range_start
#         new_end = update.date_range_end or record.date_range_end
#         validate_date_range(new_start, new_end)
#         record.date_range_start = new_start
#         record.date_range_end = new_end
#         # Re-fetch weather
#         if new_start and new_end:
#             weather_data = await fetch_forecast(record.location, new_start, new_end)
#         else:
#             weather_data = await fetch_current_weather(record.location)
#         record.temperature = weather_data["temperature"]
#         record.weather_description = weather_data["description"]
#     if update.temperature:
#         record.temperature = update.temperature
#     if update.weather_description:
#         record.weather_description = update.weather_description
#     db.commit()
#     db.refresh(record)
#     return WeatherResponse.model_validate(record)

# def delete_weather(weather_id: int, db: Session):
#     record = db.query(WeatherRecord).filter(WeatherRecord.id == weather_id).first()
#     if not record:
#         raise HTTPException(status_code=404, detail="Record not found")
#     db.delete(record)
#     db.commit()
#     return {"detail": "Record deleted"}

# def export_data(format: str, db: Session):
#     records = get_weathers(db)
#     clean_records = [r.model_dump() for r in records]
#     if format == "json":
#         return json.dumps(clean_records, default=str, indent=2)
#     elif format == "csv":
#         output = StringIO()
#         writer = csv.writer(output)
#         if clean_records:
#             writer.writerow(clean_records[0].keys())
#             for r in clean_records:
#                 writer.writerow(r.values())
#         return output.getvalue()
#     elif format == "pdf":
#         pdf = FPDF()
#         pdf.add_page()
#         pdf.set_font("Arial", size=12)
#         headers = ["ID", "Location", "Start Date", "End Date", "Temperature", "Description"]
#         pdf.cell(200, 10, txt="Weather Records", ln=1, align="C")
#         for header in headers:
#             pdf.cell(30, 10, header, 1)
#         pdf.ln()
#         for r in clean_records:
#             pdf.cell(30, 10, str(r["id"]), 1)
#             pdf.cell(30, 10, r["location"], 1)
#             pdf.cell(30, 10, str(r["date_range_start"]), 1)
#             pdf.cell(30, 10, str(r["date_range_end"]), 1)
#             pdf.cell(30, 10, str(r["temperature"]), 1)
#             pdf.cell(30, 10, r["weather_description"], 1)
#             pdf.ln()
#         bio = BytesIO()
#         bio.write(pdf.output(dest='S').encode('latin1'))
#         bio.seek(0)
#         return StreamingResponse(bio, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=weather_records.pdf"})
#     elif format == "xml":
#         root = ET.Element("weather_records")
#         for r in clean_records:
#             record_elem = ET.SubElement(root, "record")
#             for k, v in r.items():
#                 child = ET.SubElement(record_elem, k)
#                 child.text = str(v)
#         xml_str = ET.tostring(root, encoding='unicode', method='xml')
#         return xml_str
#     elif format == "markdown":
#         if not clean_records:
#             return "No records found."
#         headers = list(clean_records[0].keys())
#         md = "| " + " | ".join(headers) + " |\n"
#         md += "| " + "--- | " * len(headers) + "\n"
#         for r in clean_records:
#             md += "| " + " | ".join(str(v) for v in r.values()) + " |\n"
#         return md