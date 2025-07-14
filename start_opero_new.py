#!/usr/bin/env python3
"""
🚀 Opero Development Server
Professional development server with hot-reload, auto-opening dashboard, and comprehensive monitoring
"""
import os
import sys
import time
import uvicorn
import asyncio
import subprocess
import webbrowser
from pathlib import Path
from uvicorn_config import dev_config


def print_startup_banner():
    """Print professional startup banner"""
    print("\n" + "="*80)
    print("🚀 OPERO PLATFORM - DEVELOPMENT SERVER")
    print("="*80)
    print("🎯 AI-Powered Business Automation Platform")
    print("✨ Streamline. Automate. Excel.")
    print("-"*80)


def print_server_info():
    """Print server information"""
    print("🌐 Server Information:")
    print(f"   📍 Local URL: http://{dev_config.host}:{dev_config.port}")
    print(f"   📋 API Docs: http://{dev_config.host}:{dev_config.port}/docs")
    print(f"   📄 ReDoc: http://{dev_config.host}:{dev_config.port}/redoc")
    print(f"   🎮 Dashboard: http://{dev_config.host}:{dev_config.port}/dashboard")
    print()


def print_development_features():
    """Print development features"""
    print("🔧 Development Features:")
    print("   🔄 Hot-reload enabled for instant changes")
    print(f"   📝 Watching: {', '.join(dev_config.get_reload_includes())}")
    print("   🎯 Auto-opening dashboard for immediate testing")
    print("   📊 Comprehensive logging for easy debugging")
    print("   ⚡ Live reload on save - see changes instantly!")
    print()


def check_environment():
    """Check if environment is ready"""
    print("🔍 Environment Check:")
    
    # Check if app directory exists
    app_dir = Path("app")
    if not app_dir.exists():
        print("   ❌ App directory not found")
        return False
    print("   ✅ App directory found")
    
    # Check if main.py exists
    main_py = app_dir / "main.py"
    if not main_py.exists():
        print("   ❌ app/main.py not found")
        return False
    print("   ✅ Main application file found")
    
    # Check if dashboard exists
    dashboard = Path("dashboard.html")
    if not dashboard.exists():
        print("   ⚠️  Dashboard.html not found (optional)")
    else:
        print("   ✅ Dashboard file found")
    
    # Check Python version
    python_version = sys.version_info
    print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    print("   ✅ Environment ready!")
    print()
    return True


def open_dashboard():
    """Open dashboard in default browser"""
    try:
        print("🎮 Opening dashboard in your default browser...")
        dashboard_url = f"http://{dev_config.host}:{dev_config.port}/dashboard"
        webbrowser.open(dashboard_url)
        print("   ✅ Dashboard opened successfully!")
        print(f"   🔗 Dashboard URL: {dashboard_url}")
    except Exception as e:
        print(f"   ⚠️  Could not auto-open dashboard: {e}")
        print(f"   💡 Manually open: http://{dev_config.host}:{dev_config.port}/dashboard")
    print()


def wait_for_server(max_attempts=15):
    """Wait for server to be ready"""
    try:
        import requests
    except ImportError:
        print("   ⚠️  requests not available, skipping server readiness check")
        return True
    
    print("⏳ Waiting for server to start...")
    server_url = f"http://{dev_config.host}:{dev_config.port}/health"
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(server_url, timeout=3)
            if response.status_code == 200:
                print("   ✅ Server is ready and responding!")
                return True
        except:
            pass
        
        print(f"   🔄 Attempt {attempt + 1}/{max_attempts}...")
        time.sleep(1)
    
    print("   ⚠️  Server startup timeout, but continuing...")
    return False


async def start_server_async():
    """Start server asynchronously for better control"""
    config = uvicorn.Config(**dev_config.get_uvicorn_config())
    server = uvicorn.Server(config)
    
    # Schedule dashboard opening after a short delay
    async def delayed_dashboard_open():
        await asyncio.sleep(3)  # Wait for server to be ready
        open_dashboard()
    
    # Start dashboard opening task
    asyncio.create_task(delayed_dashboard_open())
    
    # Start the server
    await server.serve()


def main():
    """Main function to start the development server"""
    print_startup_banner()
    
    # Environment check
    if not check_environment():
        print("❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    print_server_info()
    print_development_features()
    
    # Print configuration details
    dev_config.print_config_info()
    
    print("🚀 Starting Opero development server...")
    print("   📝 Press Ctrl+C to stop the server")
    print("   🔄 Server will auto-restart on file changes")
    print("   💾 Save any file to see instant hot-reload!")
    print("   🎯 Dashboard will open automatically...")
    print()
    
    try:
        # Start server with comprehensive configuration
        asyncio.run(start_server_async())
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Opero development server...")
        print("   📊 Session completed successfully")
        print("   👋 Thanks for using Opero! See you next time.")
        print("   💡 Tip: Your changes are auto-saved and ready for deployment!")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        print("   🔧 Check the error details above and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()
