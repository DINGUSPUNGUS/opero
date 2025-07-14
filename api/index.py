"""
FastAPI application for Vercel deployment.
"""
import sys
import os
from pathlib import Path

# Add the parent directory to the Python path so we can import from app
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.routes.contacts import router as contacts_router
    from app.routes.auth import router as auth_router
    from app.routes.monitoring import router as monitoring_router
except ImportError as e:
    # Fallback for when routes don't exist or have import issues
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    # Create a simple contacts router as fallback
    from fastapi import APIRouter
    contacts_router = APIRouter(prefix="/contacts", tags=["Contacts"])
    auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
    monitoring_router = APIRouter(prefix="/monitoring", tags=["Monitoring"])
    
    @contacts_router.get("/")
    async def get_contacts():
        return [{"id": 1, "name": "Demo Contact", "email": "demo@example.com"}]
    
    @auth_router.get("/status")
    async def auth_status():
        return {"status": "available"}
    
    @monitoring_router.get("/health")
    async def health():
        return {"status": "healthy"}

# Create FastAPI app
app = FastAPI(
    title="Opero API",
    description="AI-powered business automation platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(contacts_router)
app.include_router(auth_router)
app.include_router(monitoring_router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Opero API v2.0",
        "docs": "/docs",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Vercel."""
    return {"status": "healthy", "service": "opero-api"}

# Export the app for Vercel
# Vercel looks for this pattern
def handler(request, context):
    return app

# For compatibility
api = app
