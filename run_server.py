#!/usr/bin/env python3
"""
🚀 Simple Opero Development Server
Clean and reliable development server startup
"""
import os
import sys
import uvicorn
import webbrowser
import time
import threading
from pathlib import Path

def open_dashboard():
    """Open dashboard after server starts"""
    time.sleep(3)  # Wait for server to start
    try:
        webbrowser.open("http://127.0.0.1:8000/dashboard")
        print("🎮 Dashboard opened in browser!")
    except Exception as e:
        print(f"⚠️  Could not open dashboard: {e}")

def main():
    """Start the development server"""
    print("\n" + "="*60)
    print("🚀 OPERO DEVELOPMENT SERVER")
    print("="*60)
    print("🎯 AI-Powered Business Automation Platform")
    print("✨ Streamline. Automate. Excel.")
    print("="*60)
    
    print("\n🌐 Server URLs:")
    print("   🚀 API: http://127.0.0.1:8000")
    print("   📋 Docs: http://127.0.0.1:8000/docs")
    print("   🎮 Dashboard: http://127.0.0.1:8000/dashboard")
    
    print("\n⚡ Features:")
    print("   🔄 Hot-reload enabled")
    print("   📝 Auto-restart on changes")
    print("   🎯 Dashboard auto-opens")
    
    print("\n🚀 Starting server...\n")
    
    # Set up Python path
    current_dir = str(Path(__file__).parent)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Start dashboard in background
    dashboard_thread = threading.Thread(target=open_dashboard)
    dashboard_thread.daemon = True
    dashboard_thread.start()
    
    # Start server
    try:
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            reload_dirs=["app/", "."],
            reload_includes=["*.py", "*.html", "*.css", "*.js"],
            log_level="info",
            access_log=True,
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped. Thanks for using Opero!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
