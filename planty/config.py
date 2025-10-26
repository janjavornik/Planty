"""Configuration management for Planty."""
from __future__ import annotations

import os
from typing import Any


class Config:
    """Configuration class for Planty."""
    
    def __init__(self) -> None:
        """Initialize configuration."""
        self.log_level = os.getenv("LOG_LEVEL", "info").lower()
        self.auto_create_dashboard = os.getenv("AUTO_CREATE_DASHBOARD", "true").lower() == "true"
        self.image_storage_path = os.getenv("IMAGE_STORAGE_PATH", "/share/planty/images")
        self.backup_enabled = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
        self.backup_interval = int(os.getenv("BACKUP_INTERVAL", "24"))
        
        # Home Assistant connection
        self.supervisor_token = os.getenv("SUPERVISOR_TOKEN", "")
        self.homeassistant_url = os.getenv("HOMEASSISTANT_URL", "http://supervisor/core")
        
        # Service configuration
        self.host = "0.0.0.0"
        self.port = 8100
        self.data_dir = "/data/planty"
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.image_storage_path, exist_ok=True)
    
    @property
    def headers(self) -> dict[str, str]:
        """Get headers for Home Assistant API requests."""
        return {
            "Authorization": f"Bearer {self.supervisor_token}",
            "Content-Type": "application/json"
        }


# Global config instance
config = Config()
