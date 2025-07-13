#!/usr/bin/env python3
"""
Simple script to start the FastAPI server.
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Starting AirAiBE FastAPI server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation will be available at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
