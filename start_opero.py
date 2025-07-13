"""
Opero API v2.0
AI-Powered Business Automation Platform
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting Opero API v2.0...")
    print("📊 Dashboard: Open dashboard.html in your browser")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🔥 Server: http://localhost:8000")
    print("\n💡 Tagline: Streamline. Automate. Excel.\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
