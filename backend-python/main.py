"""AlgoVisual Backend - Clean entry point"""
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router
from routes.custom import router as custom_router

app = FastAPI(title="AlgoVisual API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)
app.include_router(custom_router, prefix="/api/custom", tags=["custom"])

@app.get("/")
async def root():
    return {"message": "AlgoVisual API", "version": "2.0.0"}
