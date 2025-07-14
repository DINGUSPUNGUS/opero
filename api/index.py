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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel

# Simple contacts router without database dependencies
contacts_router = APIRouter(prefix="/contacts", tags=["Contacts"])

class ContactCreate(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None

class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    position: Optional[str]
    notes: Optional[str]
    tags: Optional[str]
    is_active: bool

# Demo data
demo_contacts = [
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe", 
        "email": "john@example.com",
        "phone": "+1-555-0123",
        "company": "Tech Corp",
        "position": "CEO",
        "notes": "Important client",
        "tags": "client,important",
        "is_active": True
    },
    {
        "id": 2,
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com", 
        "phone": "+1-555-0124",
        "company": "Design Studio",
        "position": "Creative Director",
        "notes": "Potential partner",
        "tags": "partner,creative",
        "is_active": True
    }
]

@contacts_router.get("/", response_model=List[ContactResponse])
async def get_contacts():
    """Get all contacts."""
    return demo_contacts

@contacts_router.post("/", response_model=ContactResponse)
async def create_contact(contact: ContactCreate):
    """Create a new contact."""
    new_contact = {
        "id": len(demo_contacts) + 1,
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "email": contact.email,
        "phone": contact.phone,
        "company": contact.company,
        "position": contact.position,
        "notes": contact.notes,
        "tags": contact.tags,
        "is_active": True
    }
    demo_contacts.append(new_contact)
    return new_contact

@contacts_router.get("/stats/overview")
async def get_contact_stats():
    """Get contact statistics."""
    total_contacts = len(demo_contacts)
    active_contacts = len([c for c in demo_contacts if c["is_active"]])
    companies = len(set(c["company"] for c in demo_contacts if c["company"]))
    
    return {
        "total_contacts": total_contacts,
        "active_contacts": active_contacts,
        "inactive_contacts": total_contacts - active_contacts,
        "unique_companies": companies
    }

# Simple auth router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.get("/status")
async def auth_status():
    return {"status": "available", "message": "Authentication endpoints ready"}

# Simple monitoring router
monitoring_router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

@monitoring_router.get("/health")
async def health():
    return {"status": "healthy", "service": "opero-api", "version": "2.0.0"}

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
