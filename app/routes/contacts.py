"""
Contact management routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/contacts", tags=["Contacts"])

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

class ContactFilter(BaseModel):
    company: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = True

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

@router.get("/", response_model=List[ContactResponse])
async def get_contacts(db: AsyncSession = Depends(get_db)):
    """Get all contacts."""
    return demo_contacts

@router.post("/", response_model=ContactResponse)
async def create_contact(contact: ContactCreate, db: AsyncSession = Depends(get_db)):
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

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific contact."""
    contact = next((c for c in demo_contacts if c["id"] == contact_id), None)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int, 
    contact_update: ContactUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update a contact."""
    contact = next((c for c in demo_contacts if c["id"] == contact_id), None)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Update only provided fields
    update_data = contact_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        contact[field] = value
    
    return contact

@router.delete("/{contact_id}")
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a contact."""
    contact_index = next((i for i, c in enumerate(demo_contacts) if c["id"] == contact_id), None)
    if contact_index is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    demo_contacts.pop(contact_index)
    return {"message": "Contact deleted successfully"}

@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(
    q: Optional[str] = None,
    company: Optional[str] = None,
    tags: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
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

@router.get("/stats/overview")
async def get_contact_stats(db: AsyncSession = Depends(get_db)):
    """Get contact statistics and overview."""
    total_contacts = len(demo_contacts)
    active_contacts = len([c for c in demo_contacts if c["is_active"]])
    companies = len(set(c["company"] for c in demo_contacts if c["company"]))
    
    return {
        "total_contacts": total_contacts,
        "active_contacts": active_contacts,
        "inactive_contacts": total_contacts - active_contacts,
        "unique_companies": companies,
        "contacts_by_company": {
            c["company"]: len([contact for contact in demo_contacts if contact["company"] == c["company"]])
            for c in demo_contacts if c["company"]
        }
    }
