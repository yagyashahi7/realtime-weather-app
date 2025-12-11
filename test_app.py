import requests
import json

BASE_URL = "http://127.0.0.1:8000/weather/"

# Test GET all
response = requests.get(BASE_URL)
print("GET /weather/:", response.status_code, response.json())

# Test POST (valid)
valid_data = {"location": "New York"}
response = requests.post(BASE_URL, json=valid_data)
print("POST /weather/ valid:", response.status_code, response.json())

# Test POST (invalid - missing location)
invalid_data = {}
response = requests.post(BASE_URL, json=invalid_data)
status = response.status_code
detail = response.json() if status != 422 else "422: Validation error (missing location)"
print(f"POST /weather/ invalid: {status} {detail}")

# Test GET by ID (replace 1 with actual ID from previous POST)
response = requests.get(f"{BASE_URL}1")
print("GET /weather/1:", response.status_code, response.json())

# Test PUT (update location or dates; replace 1 with ID)
update_data = {"location": "Paris"}  # Or {"date_range_start": "2025-12-09", "date_range_end": "2025-12-13"}
response = requests.put(f"{BASE_URL}1", json=update_data)
print("PUT /weather/1:", response.status_code, response.json())

# Test DELETE (replace 1 with ID)
response = requests.delete(f"{BASE_URL}1")
print("DELETE /weather/1:", response.status_code, response.json())

# Test EXPORT JSON
response = requests.get(f"{BASE_URL}export/json")
print("GET /export/json:", response.status_code)
if response.status_code == 200:
    print(json.dumps(json.loads(response.text), indent=2))

# Test EXPORT PDF (save to file)
response = requests.get(f"{BASE_URL}export/pdf")
if response.status_code == 200:
    with open("weather_records.pdf", "wb") as f:
        f.write(response.content)
    print("PDF exported to weather_records.pdf")
else:
    print("GET /export/pdf:", response.status_code)

# Test EXPORT XML
response = requests.get(f"{BASE_URL}export/xml")
print("GET /export/xml:", response.status_code, response.text if response.status_code == 200 else response.json())

# Test EXPORT Markdown
response = requests.get(f"{BASE_URL}export/markdown")
print("GET /export/markdown:", response.status_code, response.text if response.status_code == 200 else response.json())