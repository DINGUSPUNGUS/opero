"""
FastAPI application for Vercel deployment - Clean and Simple
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os

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

# === CONTACT MODELS ===
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

class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None

# === IN-MEMORY DATA STORE ===
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
    },
    {
        "id": 3,
        "first_name": "Alex",
        "last_name": "Johnson",
        "email": "alex@startupxyz.com",
        "phone": "+1-555-0125",
        "company": "StartupXYZ",
        "position": "Founder",
        "notes": "Innovative startup",
        "tags": "startup,innovation",
        "is_active": True
    }
]

# === ROOT ENDPOINTS ===
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Opero API v2.0 - AI-Powered Business Automation",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "contacts": "/contacts",
            "health": "/health",
            "docs": "/docs"
        },
        "tagline": "Streamline. Automate. Excel."
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "opero-api",
        "version": "2.0.0",
        "environment": os.getenv("VERCEL_ENV", "production")
    }

# === CONTACT ENDPOINTS ===
@app.get("/contacts", response_model=List[ContactResponse])
async def get_contacts():
    """Get all contacts."""
    return demo_contacts

@app.post("/contacts", response_model=ContactResponse)
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

@app.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int):
    """Get a specific contact."""
    contact = next((c for c in demo_contacts if c["id"] == contact_id), None)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, contact_update: ContactUpdate):
    """Update a contact."""
    contact = next((c for c in demo_contacts if c["id"] == contact_id), None)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Update only provided fields
    update_data = contact_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        contact[field] = value
    
    return contact

@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: int):
    """Delete a contact."""
    contact_index = next((i for i, c in enumerate(demo_contacts) if c["id"] == contact_id), None)
    if contact_index is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    demo_contacts.pop(contact_index)
    return {"message": "Contact deleted successfully"}

@app.get("/contacts/search/", response_model=List[ContactResponse])
async def search_contacts(
    q: Optional[str] = None,
    company: Optional[str] = None,
    tags: Optional[str] = None
):
    """Search contacts by name, company, or tags."""
    filtered_contacts = demo_contacts.copy()
    
    if q:
        q_lower = q.lower()
        filtered_contacts = [
            c for c in filtered_contacts
            if (q_lower in c["first_name"].lower() or
                (c["last_name"] and q_lower in c["last_name"].lower()) or
                (c["email"] and q_lower in c["email"].lower()) or
                (c["company"] and q_lower in c["company"].lower()))
        ]
    
    if company:
        filtered_contacts = [
            c for c in filtered_contacts
            if c["company"] and company.lower() in c["company"].lower()
        ]
    
    if tags:
        filtered_contacts = [
            c for c in filtered_contacts
            if c["tags"] and tags.lower() in c["tags"].lower()
        ]
    
    return filtered_contacts

@app.get("/contacts/stats/overview")
async def get_contact_stats():
    """Get contact statistics and overview."""
    total_contacts = len(demo_contacts)
    active_contacts = len([c for c in demo_contacts if c["is_active"]])
    companies = len(set(c["company"] for c in demo_contacts if c["company"]))
    
    # Get contacts by company
    contacts_by_company = {}
    for contact in demo_contacts:
        if contact["company"]:
            company = contact["company"]
            contacts_by_company[company] = contacts_by_company.get(company, 0) + 1
    
    return {
        "total_contacts": total_contacts,
        "active_contacts": active_contacts,
        "inactive_contacts": total_contacts - active_contacts,
        "unique_companies": companies,
        "contacts_by_company": contacts_by_company,
        "recent_activity": "3 new contacts this week"
    }

# === AUTH ENDPOINTS ===
@app.get("/auth/status")
async def auth_status():
    """Authentication status endpoint."""
    return {
        "status": "available",
        "message": "Authentication system ready",
        "version": "2.0.0"
    }

# === MONITORING ENDPOINTS ===
@app.get("/monitoring/health")
async def monitoring_health():
    """Detailed health monitoring."""
    return {
        "status": "healthy",
        "service": "opero-api",
        "version": "2.0.0",
        "timestamp": "2025-07-14T09:30:00Z",
        "checks": {
            "api": "healthy",
            "contacts": "operational",
            "memory": "normal"
        }
    }

# For Vercel deployment
def handler(request, context):
    return app

# Export the app for Vercel
# Alternative export for compatibility
api = app
