"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.routes.auth import router as auth_router
from app.routes.contacts import router as contacts_router
from app.routes.agent import router as agent_router
from app.routes.monitoring import router as monitoring_router

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
app.include_router(monitoring_router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Opero API v2.0 - AI-Powered Business Automation",
        "status": "operational",
        "docs": "/docs",
        "tagline": "Streamline. Automate. Excel."
    }

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard HTML page."""
    dashboard_path = Path(__file__).parent.parent / "dashboard.html"
    if dashboard_path.exists():
        return HTMLResponse(content=dashboard_path.read_text(encoding='utf-8'))
    else:
        return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)

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
