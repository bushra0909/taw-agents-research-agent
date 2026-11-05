from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Application settings
APP_NAME = os.getenv("APP_NAME", "Company Research Agent")

# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    description="An AI-powered company research and PDF brief generator.",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to Company Research Agent",
        "status": "running",
        "project": APP_NAME
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }