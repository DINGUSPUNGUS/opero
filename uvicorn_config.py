"""
Uvicorn configuration for hot-reload development with comprehensive file watching
"""
import os
from typing import List, Dict, Any
from pathlib import Path


class DevelopmentConfig:
    """Development server configuration for Opero platform"""
    
    def __init__(self):
        self.app_dir = Path(__file__).parent
        self.host = "127.0.0.1"
        self.port = 8000
        self.app_module = "app.main:app"
        self.log_level = "info"
        
    def get_reload_dirs(self) -> List[str]:
        """Get directories to watch for file changes"""
        return [
            str(self.app_dir / "app"),
            str(self.app_dir),  # Root for dashboard.html and config files
        ]
    
    def get_reload_includes(self) -> List[str]:
        """Get file patterns to watch for changes"""
        return [
            "*.py",     # Python files
            "*.html",   # HTML templates
            "*.css",    # Stylesheets
            "*.js",     # JavaScript files
            "*.json",   # JSON config files
            "*.yml",    # YAML config files
            "*.yaml",   # YAML config files
            "*.toml",   # TOML config files
        ]
    
    def get_reload_excludes(self) -> List[str]:
        """Get patterns to exclude from watching"""
        return [
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "__pycache__",
            ".git",
            ".vscode",
            "venv",
            ".env",
            "*.log",
            "*.sqlite",
            "*.db",
        ]
    
    def get_uvicorn_config(self) -> Dict[str, Any]:
        """Get complete uvicorn configuration"""
        return {
            "app": self.app_module,
            "host": self.host,
            "port": self.port,
            "reload": True,
            "reload_dirs": self.get_reload_dirs(),
            "reload_includes": self.get_reload_includes(),
            "reload_excludes": self.get_reload_excludes(),
            "log_level": self.log_level,
            "access_log": True,
            "use_colors": True,
            "loop": "auto",
            "interface": "auto",
        }
    
    def print_config_info(self):
        """Print development server configuration"""
        print("🔧 Development Server Configuration:")
        print(f"   📁 Reload Directories: {', '.join(self.get_reload_dirs())}")
        print(f"   📄 Watching File Types: {', '.join(self.get_reload_includes())}")
        print(f"   🚫 Excluding: {', '.join(self.get_reload_excludes())}")
        print(f"   🌐 Server: http://{self.host}:{self.port}")
        print()


# Global config instance
dev_config = DevelopmentConfig()
