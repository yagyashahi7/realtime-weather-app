# from fastapi import FastAPI
# from routers.weather import router as weather_router
# from fastapi.responses import RedirectResponse

# app = FastAPI(title="Weather App Backend by Yagya Bahadur Shahi")

# app.include_router(weather_router, prefix="/weather")

# @app.get("/info")
# async def info():
#     return {
#         "description": "Weather App Backend by Yagya Bahadur Shahi. Learn more at Product Manager Accelerator on LinkedIn."
#     }

# @app.get("/", include_in_schema=False)
# async def root():
#     return RedirectResponse(url="/docs")  # Or return {"message": "Welcome to Weather App Backend. Visit /docs for API documentation."}


# from fastapi import FastAPI
# from routers.weather import router as weather_router
# from fastapi.responses import RedirectResponse
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI(title="Weather App Backend by Yagya Bahadur Shahi")

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allow all origins for dev; specify frontend URL in prod
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(weather_router, prefix="/weather")

# @app.get("/info")
# async def info():
#     return {
#         "description": "Weather App Backend by Yagya Bahadur Shahi. Learn more at Product Manager Accelerator on LinkedIn."
#     }

# @app.get("/", include_in_schema=False)
# async def root():
#     return RedirectResponse(url="/docs")
from fastapi import FastAPI
from routers.weather import router as weather_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Weather App Backend by Yagya Bahadur Shahi")

# Add CORS middleware (restricted for security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "file://*"],  # Local dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather_router, prefix="/weather")

@app.get("/info")
async def info():
    return {
        "description": "Weather App Backend by Yagya Bahadur Shahi. Learn more at Product Manager Accelerator on LinkedIn."
    }

# Serve frontend statically at root
app.mount("/", StaticFiles(directory="weather_app_frontend", html=True), name="frontend")