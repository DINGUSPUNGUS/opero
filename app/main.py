"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router
from app.routes.contacts import router as contacts_router
from app.routes.agent import router as agent_router

# Create FastAPI app
app = FastAPI(
    title="Opero API",
    description="AI-powered business automation platform - Streamline your operations with intelligent automation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(contacts_router)
app.include_router(agent_router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Opero API v2.0 - AI-Powered Business Automation",
        "status": "operational",
        "docs": "/docs",
        "tagline": "Streamline. Automate. Excel."
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/info")
async def app_info():
    """Application info endpoint."""
    return {
        "name": "Opero",
        "version": "2.0.0",
        "description": "AI-powered business automation platform",
        "tagline": "Streamline. Automate. Excel.",
        "features": [
            "Intelligent Contact Management",
            "AI-Powered Task Automation", 
            "Smart Email & Communication",
            "Advanced Analytics & Reporting",
            "Multi-tenant Architecture",
            "Real-time Collaboration"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/auth",
            "contacts": "/contacts",
            "agent": "/agent"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
