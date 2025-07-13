"""
AI Agent routes for handling user interactions.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.ai_agent import agent_service, AgentRequest, AgentResponse, TaskRequest, TaskResponse
from typing import List

router = APIRouter(prefix="/agent", tags=["AI Agent"])

@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(
    request: AgentRequest,
    db: AsyncSession = Depends(get_db)
):
    """Chat with the AI agent."""
    try:
        response = await agent_service.process_request(request)
        
        # Update user context
        await agent_service.update_user_context(
            request.user_id, 
            {
                "last_request": request.message,
                "last_response": response.response,
                "timestamp": response.timestamp.isoformat()
            }
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")

@router.get("/capabilities")
async def get_agent_capabilities():
    """Get AI agent capabilities."""
    return {
        "capabilities": agent_service.capabilities,
        "description": "AI-powered business automation assistant",
        "supported_domains": [
            "contact_management",
            "email_automation",
            "calendar_scheduling", 
            "document_generation",
            "data_analysis"
        ]
    }

@router.get("/context/{user_id}")
async def get_user_context(user_id: int):
    """Get user conversation context."""
    context = await agent_service.get_user_context(user_id)
    return {"user_id": user_id, "context": context}

@router.post("/demo")
async def demo_conversation():
    """Demo conversation with the agent."""
    demo_requests = [
        "Help me manage my contacts",
        "I need to schedule a meeting",
        "Can you help me with email automation?",
        "What are your capabilities?"
    ]
    
    responses = []
    for i, message in enumerate(demo_requests):
        request = AgentRequest(user_id=999, message=message, agent_type="demo")
        response = await agent_service.process_request(request)
        responses.append({
            "request": message,
            "response": response.response,
            "actions": response.actions
        })
    
    return {"demo_conversation": responses}

@router.post("/task", response_model=TaskResponse)
async def execute_task(
    task: TaskRequest,
    db: AsyncSession = Depends(get_db)
):
    """Execute a specific business task."""
    try:
        response = await agent_service.execute_task(task)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task execution error: {str(e)}")

@router.get("/tasks/templates")
async def get_task_templates():
    """Get available task templates."""
    return {
        "templates": [
            {
                "type": "contact_analysis",
                "name": "Contact Analysis Report",
                "description": "Analyze contact patterns and generate insights",
                "parameters": ["date_range", "company_filter"]
            },
            {
                "type": "email_draft", 
                "name": "Email Draft Generator",
                "description": "Generate professional email drafts",
                "parameters": ["recipient", "purpose", "tone"]
            },
            {
                "type": "meeting_schedule",
                "name": "Smart Meeting Scheduler", 
                "description": "Schedule meetings with intelligent suggestions",
                "parameters": ["participant", "duration", "urgency"]
            },
            {
                "type": "report_generation",
                "name": "Business Report Generator",
                "description": "Generate comprehensive business reports",
                "parameters": ["type", "period", "metrics"]
            }
        ]
    }

@router.get("/analytics")
async def get_agent_analytics():
    """Get AI agent usage analytics."""
    return {
        "usage_stats": {
            "total_conversations": 147,
            "tasks_completed": 89,
            "success_rate": "94%",
            "avg_response_time": "1.2s"
        },
        "popular_features": [
            {"feature": "Contact Management", "usage": "35%"},
            {"feature": "Email Automation", "usage": "28%"},
            {"feature": "Meeting Scheduling", "usage": "22%"}, 
            {"feature": "Report Generation", "usage": "15%"}
        ],
        "user_satisfaction": 4.7,
        "efficiency_gains": {
            "time_saved": "12.5 hours/week",
            "automation_rate": "78%",
            "manual_tasks_reduced": "65%"
        }
    }
