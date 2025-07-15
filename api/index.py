"""
Substrata.AI - Conservation & NPO Platform API
Enhanced FastAPI application for conservation organizations
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
import os

# Create FastAPI app
app = FastAPI(
    title="Substrata.AI API",
    description="Conservation & NPO Management Platform - Empowering environmental organizations with AI-driven tools",
    version="1.0.0",
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

# === ENUMS ===
class SpeciesType(str, Enum):
    MAMMAL = "mammal"
    BIRD = "bird"
    REPTILE = "reptile"
    AMPHIBIAN = "amphibian"
    FISH = "fish"
    INSECT = "insect"
    PLANT = "plant"
    FUNGI = "fungi"
    OTHER = "other"

class ConservationStatus(str, Enum):
    CRITICALLY_ENDANGERED = "critically_endangered"
    ENDANGERED = "endangered"
    VULNERABLE = "vulnerable"
    NEAR_THREATENED = "near_threatened"
    LEAST_CONCERN = "least_concern"
    DATA_DEFICIENT = "data_deficient"
    NOT_EVALUATED = "not_evaluated"

class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class StakeholderType(str, Enum):
    DONOR = "donor"
    VOLUNTEER = "volunteer"
    PARTNER = "partner"
    GOVERNMENT = "government"
    RESEARCHER = "researcher"
    COMMUNITY = "community"

# === PYDANTIC MODELS ===

# Field Survey Models
class FieldSurveyCreate(BaseModel):
    species_name: str = Field(..., description="Name of the species observed")
    species_type: SpeciesType
    conservation_status: Optional[ConservationStatus] = None
    count: int = Field(..., ge=0, description="Number of individuals observed")
    location_name: str = Field(..., description="Location name or description")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = None
    weather_conditions: Optional[str] = None
    habitat_description: Optional[str] = None
    behavior_notes: Optional[str] = None
    observer_name: str
    observation_date: str  # Using string to avoid datetime parsing issues in serverless
    photo_urls: Optional[List[str]] = []
    tags: Optional[List[str]] = []

class FieldSurveyResponse(BaseModel):
    id: int
    species_name: str
    species_type: SpeciesType
    conservation_status: Optional[ConservationStatus]
    count: int
    location_name: str
    latitude: float
    longitude: float
    altitude: Optional[float]
    weather_conditions: Optional[str]
    habitat_description: Optional[str]
    behavior_notes: Optional[str]
    observer_name: str
    observation_date: str
    photo_urls: List[str]
    tags: List[str]
    created_at: str

# Conservation Project Models
class ConservationProjectCreate(BaseModel):
    name: str = Field(..., description="Project name")
    description: str
    location: str
    start_date: str
    end_date: Optional[str] = None
    budget: Optional[float] = Field(None, ge=0)
    funding_source: Optional[str] = None
    project_lead: str
    status: ProjectStatus = ProjectStatus.PLANNING
    goals: List[str] = []
    species_focus: Optional[List[str]] = []
    habitat_type: Optional[str] = None

class ConservationProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    location: str
    start_date: str
    end_date: Optional[str]
    budget: Optional[float]
    funding_source: Optional[str]
    project_lead: str
    status: ProjectStatus
    goals: List[str]
    species_focus: List[str]
    habitat_type: Optional[str]
    created_at: str
    updated_at: str

# Stakeholder Models (Enhanced from your original contacts)
class StakeholderCreate(BaseModel):
    name: str = Field(..., description="Full name")
    email: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
    stakeholder_type: StakeholderType
    expertise: Optional[List[str]] = []
    location: Optional[str] = None
    notes: Optional[str] = None
    donation_history: Optional[List[Dict[str, Any]]] = []
    volunteer_skills: Optional[List[str]] = []
    availability: Optional[str] = None

class StakeholderResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    organization: Optional[str]
    stakeholder_type: StakeholderType
    expertise: List[str]
    location: Optional[str]
    notes: Optional[str]
    donation_history: List[Dict[str, Any]]
    volunteer_skills: List[str]
    availability: Optional[str]
    created_at: str
    is_active: bool

# Grant Models
class GrantCreate(BaseModel):
    title: str
    funding_organization: str
    amount: float = Field(..., ge=0)
    application_deadline: str
    project_start: str
    project_end: str
    status: str = "applied"
    description: str
    requirements: List[str] = []
    reporting_schedule: List[str] = []

class GrantResponse(BaseModel):
    id: int
    title: str
    funding_organization: str
    amount: float
    application_deadline: str
    project_start: str
    project_end: str
    status: str
    description: str
    requirements: List[str]
    reporting_schedule: List[str]
    created_at: str

# === IN-MEMORY DATA STORES ===
demo_field_surveys = [
    {
        "id": 1,
        "species_name": "African Elephant",
        "species_type": "mammal",
        "conservation_status": "endangered",
        "count": 12,
        "location_name": "Maasai Mara National Reserve",
        "latitude": -1.4061,
        "longitude": 35.0117,
        "altitude": 1500.0,
        "weather_conditions": "Clear, 28°C",
        "habitat_description": "Open savanna with scattered acacia trees",
        "behavior_notes": "Herd moving towards water source, included 3 juveniles",
        "observer_name": "Dr. Sarah Johnson",
        "observation_date": "2025-07-10T08:30:00",
        "photo_urls": ["https://example.com/elephant1.jpg"],
        "tags": ["herd", "migration", "family_group"],
        "created_at": "2025-07-10T08:35:00"
    },
    {
        "id": 2,
        "species_name": "Baobab Tree",
        "species_type": "plant",
        "conservation_status": "vulnerable",
        "count": 1,
        "location_name": "Tsavo East National Park",
        "latitude": -2.3833,
        "longitude": 38.5167,
        "altitude": 400.0,
        "weather_conditions": "Partly cloudy, 32°C",
        "habitat_description": "Semi-arid woodland",
        "behavior_notes": "Ancient tree showing signs of drought stress",
        "observer_name": "Mark Thompson",
        "observation_date": "2025-07-12T14:15:00",
        "photo_urls": ["https://example.com/baobab1.jpg"],
        "tags": ["ancient", "drought_stress", "monitoring"],
        "created_at": "2025-07-12T14:20:00"
    },
    {
        "id": 3,
        "species_name": "Mountain Gorilla",
        "species_type": "mammal",
        "conservation_status": "critically_endangered",
        "count": 8,
        "location_name": "Bwindi Impenetrable National Park",
        "latitude": -1.0667,
        "longitude": 29.7833,
        "altitude": 2200.0,
        "weather_conditions": "Misty, 18°C",
        "habitat_description": "Dense montane rainforest",
        "behavior_notes": "Silverback-led group, peaceful foraging behavior",
        "observer_name": "Dr. Jane Goodall",
        "observation_date": "2025-07-13T10:45:00",
        "photo_urls": ["https://example.com/gorilla1.jpg"],
        "tags": ["silverback", "family_group", "foraging"],
        "created_at": "2025-07-13T11:00:00"
    }
]

demo_projects = [
    {
        "id": 1,
        "name": "Elephant Corridor Protection",
        "description": "Establishing wildlife corridors to reduce human-elephant conflict",
        "location": "Maasai Mara, Kenya",
        "start_date": "2025-01-15",
        "end_date": "2026-01-15",
        "budget": 250000.0,
        "funding_source": "Wildlife Conservation Fund",
        "project_lead": "Dr. Sarah Johnson",
        "status": "active",
        "goals": ["Reduce human-elephant conflict by 60%", "Establish 5 wildlife corridors", "Train 50 community rangers"],
        "species_focus": ["African Elephant", "Buffalo", "Zebra"],
        "habitat_type": "Savanna grassland",
        "created_at": "2025-01-10T10:00:00",
        "updated_at": "2025-07-15T09:30:00"
    },
    {
        "id": 2,
        "name": "Marine Turtle Monitoring",
        "description": "Long-term monitoring of sea turtle nesting sites and population dynamics",
        "location": "Watamu Beach, Kenya",
        "start_date": "2024-06-01",
        "end_date": "2027-05-31",
        "budget": 180000.0,
        "funding_source": "Ocean Conservation Trust",
        "project_lead": "Dr. Maria Santos",
        "status": "active",
        "goals": ["Monitor 500+ nests annually", "Reduce nest predation by 40%", "Train 30 local conservationists"],
        "species_focus": ["Green Turtle", "Hawksbill Turtle", "Olive Ridley"],
        "habitat_type": "Coastal marine",
        "created_at": "2024-05-15T14:20:00",
        "updated_at": "2025-07-15T08:15:00"
    }
]

demo_stakeholders = [
    {
        "id": 1,
        "name": "Green Earth Foundation",
        "email": "contact@greenearth.org",
        "phone": "+1-555-0123",
        "organization": "Green Earth Foundation",
        "stakeholder_type": "donor",
        "expertise": ["Environmental Law", "Grant Writing"],
        "location": "San Francisco, CA",
        "notes": "Major donor, interested in elephant conservation",
        "donation_history": [
            {"date": "2025-01-15", "amount": 50000, "project": "Elephant Corridor Protection"},
            {"date": "2024-07-20", "amount": 25000, "project": "Marine Turtle Monitoring"}
        ],
        "volunteer_skills": [],
        "availability": "Monthly meetings",
        "created_at": "2024-12-01T10:00:00",
        "is_active": True
    },
    {
        "id": 2,
        "name": "Dr. Maria Rodriguez",
        "email": "maria.rodriguez@university.edu",
        "phone": "+254-700-123456",
        "organization": "University of Nairobi",
        "stakeholder_type": "researcher",
        "expertise": ["Wildlife Biology", "Conservation Genetics"],
        "location": "Nairobi, Kenya",
        "notes": "Lead researcher on elephant genetics project",
        "donation_history": [],
        "volunteer_skills": ["Data Analysis", "Field Research", "GPS Mapping"],
        "availability": "Weekends and holidays",
        "created_at": "2025-02-15T14:30:00",
        "is_active": True
    },
    {
        "id": 3,
        "name": "James Mwangi",
        "email": "james.mwangi@gmail.com",
        "phone": "+254-722-345678",
        "organization": "Local Community Group",
        "stakeholder_type": "volunteer",
        "expertise": ["Traditional Ecological Knowledge", "Community Outreach"],
        "location": "Maasai Mara, Kenya",
        "notes": "Community ranger and wildlife guide",
        "donation_history": [],
        "volunteer_skills": ["Wildlife Tracking", "Community Education", "Swahili Translation"],
        "availability": "Full-time volunteer",
        "created_at": "2025-03-10T09:15:00",
        "is_active": True
    }
]

demo_grants = [
    {
        "id": 1,
        "title": "Wildlife Corridor Development Grant",
        "funding_organization": "National Geographic Society",
        "amount": 150000.0,
        "application_deadline": "2025-09-30",
        "project_start": "2026-01-01",
        "project_end": "2027-12-31",
        "status": "in_review",
        "description": "Funding for establishing wildlife corridors in East Africa",
        "requirements": ["Environmental Impact Assessment", "Community Consultation Report", "5-year Sustainability Plan"],
        "reporting_schedule": ["Quarterly Progress Reports", "Annual Financial Reports", "Final Impact Assessment"],
        "created_at": "2025-07-01T09:00:00"
    },
    {
        "id": 2,
        "title": "Marine Conservation Innovation Fund",
        "funding_organization": "Blue Planet Foundation",
        "amount": 75000.0,
        "application_deadline": "2025-11-15",
        "project_start": "2026-03-01",
        "project_end": "2027-02-28",
        "status": "draft",
        "description": "Support for innovative marine turtle conservation technologies",
        "requirements": ["Technology Demonstration", "Cost-Benefit Analysis", "Scalability Assessment"],
        "reporting_schedule": ["Bi-annual Progress Reports", "Technology Transfer Documentation"],
        "created_at": "2025-07-05T16:30:00"
    }
]

# === ROOT ENDPOINTS ===
@app.get("/")
async def root():
    """Root endpoint for Substrata.AI Conservation Platform."""
    return {
        "message": "Welcome to Substrata.AI - Empowering Conservation Through Technology",
        "tagline": "Data-Driven Conservation for a Sustainable Future",
        "platform": "Conservation & NPO Management",
        "version": "1.0.0",
        "features": {
            "field_surveys": "GPS-tagged wildlife & vegetation observations",
            "project_management": "Conservation project tracking & reporting",
            "stakeholder_crm": "Donor, volunteer & partner management",
            "grant_tracking": "Funding applications & compliance monitoring",
            "analytics": "Conservation impact analysis & reporting"
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "field_surveys": "/field-surveys",
            "projects": "/projects",
            "stakeholders": "/stakeholders",
            "grants": "/grants",
            "analytics": "/analytics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "substrata-ai",
        "version": "1.0.0",
        "environment": os.getenv("VERCEL_ENV", "production"),
        "modules": {
            "field_surveys": "operational",
            "project_management": "operational",
            "stakeholder_crm": "operational",
            "grant_tracking": "operational",
            "analytics": "operational"
        }
    }

# === FIELD SURVEY ENDPOINTS ===
@app.get("/field-surveys", response_model=List[FieldSurveyResponse])
async def get_field_surveys():
    """Get all field survey observations."""
    return demo_field_surveys

@app.post("/field-surveys", response_model=FieldSurveyResponse)
async def create_field_survey(survey: FieldSurveyCreate):
    """Create a new field survey observation."""
    import datetime
    new_survey = {
        "id": len(demo_field_surveys) + 1,
        **survey.dict(),
        "created_at": datetime.datetime.now().isoformat()
    }
    demo_field_surveys.append(new_survey)
    return new_survey

@app.get("/field-surveys/{survey_id}", response_model=FieldSurveyResponse)
async def get_field_survey(survey_id: int):
    """Get a specific field survey observation."""
    survey = next((s for s in demo_field_surveys if s["id"] == survey_id), None)
    if not survey:
        raise HTTPException(status_code=404, detail="Field survey not found")
    return survey

@app.get("/field-surveys/species/{species_name}")
async def get_surveys_by_species(species_name: str):
    """Get all observations for a specific species."""
    species_surveys = [s for s in demo_field_surveys if species_name.lower() in s["species_name"].lower()]
    return {
        "species": species_name,
        "total_observations": len(species_surveys),
        "total_individuals": sum(s["count"] for s in species_surveys),
        "observations": species_surveys
    }

# === CONSERVATION PROJECT ENDPOINTS ===
@app.get("/projects", response_model=List[ConservationProjectResponse])
async def get_projects():
    """Get all conservation projects."""
    return demo_projects

@app.post("/projects", response_model=ConservationProjectResponse)
async def create_project(project: ConservationProjectCreate):
    """Create a new conservation project."""
    import datetime
    now = datetime.datetime.now().isoformat()
    new_project = {
        "id": len(demo_projects) + 1,
        **project.dict(),
        "created_at": now,
        "updated_at": now
    }
    demo_projects.append(new_project)
    return new_project

@app.get("/projects/{project_id}", response_model=ConservationProjectResponse)
async def get_project(project_id: int):
    """Get a specific conservation project."""
    project = next((p for p in demo_projects if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.get("/projects/status/{status}")
async def get_projects_by_status(status: ProjectStatus):
    """Get projects by status."""
    filtered_projects = [p for p in demo_projects if p["status"] == status]
    return {
        "status": status,
        "count": len(filtered_projects),
        "projects": filtered_projects
    }

# === STAKEHOLDER ENDPOINTS (Enhanced CRM) ===
@app.get("/stakeholders", response_model=List[StakeholderResponse])
async def get_stakeholders():
    """Get all stakeholders (donors, volunteers, partners, etc.)."""
    return demo_stakeholders

@app.post("/stakeholders", response_model=StakeholderResponse)
async def create_stakeholder(stakeholder: StakeholderCreate):
    """Create a new stakeholder."""
    import datetime
    new_stakeholder = {
        "id": len(demo_stakeholders) + 1,
        **stakeholder.dict(),
        "created_at": datetime.datetime.now().isoformat(),
        "is_active": True
    }
    demo_stakeholders.append(new_stakeholder)
    return new_stakeholder

@app.get("/stakeholders/donors", response_model=List[StakeholderResponse])
async def get_donors():
    """Get all donors."""
    return [s for s in demo_stakeholders if s["stakeholder_type"] == "donor"]

@app.get("/stakeholders/volunteers", response_model=List[StakeholderResponse])
async def get_volunteers():
    """Get all volunteers."""
    return [s for s in demo_stakeholders if s["stakeholder_type"] == "volunteer"]

@app.get("/stakeholders/researchers", response_model=List[StakeholderResponse])
async def get_researchers():
    """Get all researchers."""
    return [s for s in demo_stakeholders if s["stakeholder_type"] == "researcher"]

@app.get("/stakeholders/{stakeholder_id}", response_model=StakeholderResponse)
async def get_stakeholder(stakeholder_id: int):
    """Get a specific stakeholder."""
    stakeholder = next((s for s in demo_stakeholders if s["id"] == stakeholder_id), None)
    if not stakeholder:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    return stakeholder

# === GRANT TRACKING ENDPOINTS ===
@app.get("/grants", response_model=List[GrantResponse])
async def get_grants():
    """Get all grant applications and tracking."""
    return demo_grants

@app.post("/grants", response_model=GrantResponse)
async def create_grant(grant: GrantCreate):
    """Create a new grant application."""
    import datetime
    new_grant = {
        "id": len(demo_grants) + 1,
        **grant.dict(),
        "created_at": datetime.datetime.now().isoformat()
    }
    demo_grants.append(new_grant)
    return new_grant

@app.get("/grants/{grant_id}", response_model=GrantResponse)
async def get_grant(grant_id: int):
    """Get a specific grant."""
    grant = next((g for g in demo_grants if g["id"] == grant_id), None)
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    return grant

@app.get("/grants/status/{status}")
async def get_grants_by_status(status: str):
    """Get grants by status."""
    filtered_grants = [g for g in demo_grants if g["status"] == status]
    return {
        "status": status,
        "count": len(filtered_grants),
        "total_amount": sum(g["amount"] for g in filtered_grants),
        "grants": filtered_grants
    }

# === ANALYTICS & REPORTING ENDPOINTS ===
@app.get("/analytics/species-summary")
async def get_species_summary():
    """Get summary of species observations."""
    species_count = {}
    conservation_status_count = {}
    
    for survey in demo_field_surveys:
        species = survey["species_name"]
        status = survey.get("conservation_status", "not_evaluated")
        
        if species in species_count:
            species_count[species] += survey["count"]
        else:
            species_count[species] = survey["count"]
            
        conservation_status_count[status] = conservation_status_count.get(status, 0) + 1
    
    return {
        "total_species": len(species_count),
        "total_observations": len(demo_field_surveys),
        "total_individuals": sum(species_count.values()),
        "species_breakdown": species_count,
        "conservation_status_breakdown": conservation_status_count,
        "threatened_species": [
            s for s in demo_field_surveys 
            if s.get("conservation_status") in ["critically_endangered", "endangered", "vulnerable"]
        ]
    }

@app.get("/analytics/project-overview")
async def get_project_overview():
    """Get comprehensive project overview."""
    total_budget = sum(p.get("budget", 0) for p in demo_projects)
    active_projects = [p for p in demo_projects if p["status"] == "active"]
    
    status_breakdown = {}
    for project in demo_projects:
        status = project["status"]
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    return {
        "total_projects": len(demo_projects),
        "active_projects": len(active_projects),
        "total_budget": total_budget,
        "average_project_budget": total_budget / len(demo_projects) if demo_projects else 0,
        "status_breakdown": status_breakdown,
        "projects_by_location": list(set(p["location"] for p in demo_projects))
    }

@app.get("/analytics/stakeholder-summary")
async def get_stakeholder_summary():
    """Get stakeholder analytics."""
    type_breakdown = {}
    total_donations = 0
    
    for stakeholder in demo_stakeholders:
        stakeholder_type = stakeholder["stakeholder_type"]
        type_breakdown[stakeholder_type] = type_breakdown.get(stakeholder_type, 0) + 1
        
        for donation in stakeholder.get("donation_history", []):
            total_donations += donation.get("amount", 0)
    
    return {
        "total_stakeholders": len(demo_stakeholders),
        "active_stakeholders": len([s for s in demo_stakeholders if s["is_active"]]),
        "stakeholder_type_breakdown": type_breakdown,
        "total_donations": total_donations,
        "average_donation": total_donations / sum(len(s.get("donation_history", [])) for s in demo_stakeholders) if any(s.get("donation_history") for s in demo_stakeholders) else 0
    }

@app.get("/analytics/grant-overview")
async def get_grant_overview():
    """Get grant funding analytics."""
    total_requested = sum(g["amount"] for g in demo_grants)
    status_breakdown = {}
    
    for grant in demo_grants:
        status = grant["status"]
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    return {
        "total_grants": len(demo_grants),
        "total_amount_requested": total_requested,
        "average_grant_size": total_requested / len(demo_grants) if demo_grants else 0,
        "status_breakdown": status_breakdown,
        "funding_organizations": list(set(g["funding_organization"] for g in demo_grants))
    }

@app.get("/analytics/dashboard")
async def get_dashboard_summary():
    """Get complete dashboard summary for conservation overview."""
    # Get basic counts
    total_surveys = len(demo_field_surveys)
    total_projects = len(demo_projects)
    total_stakeholders = len(demo_stakeholders)
    total_grants = len(demo_grants)
    
    # Recent activity (last 30 days simulation)
    recent_surveys = [s for s in demo_field_surveys[-5:]]  # Latest 5 for demo
    active_projects = [p for p in demo_projects if p["status"] == "active"]
    
    # Financial overview
    total_project_budget = sum(p.get("budget", 0) for p in demo_projects)
    total_grant_requests = sum(g["amount"] for g in demo_grants)
    
    return {
        "overview": {
            "total_field_surveys": total_surveys,
            "total_projects": total_projects,
            "total_stakeholders": total_stakeholders,
            "total_grants": total_grants
        },
        "recent_activity": {
            "latest_surveys": recent_surveys,
            "active_projects": active_projects
        },
        "financial": {
            "total_project_budget": total_project_budget,
            "total_grant_requests": total_grant_requests,
            "funding_gap": max(0, total_project_budget - total_grant_requests)
        },
        "conservation_impact": {
            "species_monitored": len(set(s["species_name"] for s in demo_field_surveys)),
            "locations_covered": len(set(s["location_name"] for s in demo_field_surveys)),
            "threatened_species_tracked": len([s for s in demo_field_surveys if s.get("conservation_status") in ["critically_endangered", "endangered"]])
        }
    }

# Export the app for Vercel
application = app
api = app
handler = app
