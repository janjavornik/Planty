"""Storage management for Planty."""
from __future__ import annotations

import aiofiles
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from .config import config

_LOGGER = logging.getLogger(__name__)


class PlantyStorage:
    """Handle storage for Planty data."""
    
    def __init__(self) -> None:
        """Initialize the storage handler."""
        self.storage_file = os.path.join(config.data_dir, "plants.json")
        self._data: Dict[str, Any] = {"plants": {}}
    
    async def load(self) -> Dict[str, Any]:
        """Load data from storage."""
        try:
            if os.path.exists(self.storage_file):
                async with aiofiles.open(self.storage_file, 'r') as f:
                    content = await f.read()
                    self._data = json.loads(content)
            else:
                self._data = {"plants": {}}
                await self.save()  # Create initial file
        except Exception as err:
            _LOGGER.error(f"Failed to load storage: {err}")
            self._data = {"plants": {}}
        
        return self._data
    
    async def save(self) -> None:
        """Save data to storage."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            
            async with aiofiles.open(self.storage_file, 'w') as f:
                await f.write(json.dumps(self._data, indent=2, default=str))
                
        except Exception as err:
            _LOGGER.error(f"Failed to save storage: {err}")
    
    @property
    def data(self) -> Dict[str, Any]:
        """Return the storage data."""
        return self._data
    
    def get_plant(self, plant_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific plant's data."""
        return self._data.get("plants", {}).get(plant_id)
    
    async def add_plant(self, plant_id: str, plant_data: Dict[str, Any]) -> None:
        """Add a new plant."""
        if "plants" not in self._data:
            self._data["plants"] = {}
        
        plant_data["created"] = datetime.now().isoformat()
        plant_data["modified"] = datetime.now().isoformat()
        
        self._data["plants"][plant_id] = plant_data
        await self.save()
    
    async def update_plant(self, plant_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing plant."""
        if plant_id not in self._data.get("plants", {}):
            return False
        
        updates["modified"] = datetime.now().isoformat()
        self._data["plants"][plant_id].update(updates)
        await self.save()
        return True
    
    async def remove_plant(self, plant_id: str) -> bool:
        """Remove a plant."""
        if plant_id in self._data.get("plants", {}):
            del self._data["plants"][plant_id]
            await self.save()
            return True
        return False
    
    async def water_plant(self, plant_id: str) -> bool:
        """Mark a plant as watered."""
        if plant_id in self._data.get("plants", {}):
            self._data["plants"][plant_id]["last_watered"] = datetime.now().isoformat()
            self._data["plants"][plant_id]["modified"] = datetime.now().isoformat()
            await self.save()
            return True
        return False
    
    def get_all_plants(self) -> Dict[str, Any]:
        """Get all plants."""
        return self._data.get("plants", {})


class PlantsDatabase:
    """Handle the plants database."""
    
    def __init__(self) -> None:
        """Initialize the database."""
        self.database_file = "/app/planty/data/plants_data.json"
        self._data: Dict[str, Any] = {"plants": {}}
    
    async def load(self) -> Dict[str, Any]:
        """Load the plants database."""
        try:
            if os.path.exists(self.database_file):
                async with aiofiles.open(self.database_file, 'r') as f:
                    content = await f.read()
                    self._data = json.loads(content)
            else:
                # Create default database
                self._data = await self._create_default_database()
                await self._save_database()
        except Exception as err:
            _LOGGER.error(f"Failed to load plants database: {err}")
            self._data = await self._create_default_database()
        
        return self._data
    
    async def _create_default_database(self) -> Dict[str, Any]:
        """Create a default plants database."""
        return {
            "plants": {
                "snake_plant": {
                    "name": "Snake Plant",
                    "scientific_name": "Sansevieria trifasciata",
                    "watering_interval": 14,
                    "humidity_min": 20,
                    "humidity_max": 40,
                    "care_level": "easy",
                    "description": "Low-maintenance plant that tolerates neglect and low light conditions."
                },
                "pothos": {
                    "name": "Pothos",
                    "scientific_name": "Epipremnum aureum",
                    "watering_interval": 7,
                    "humidity_min": 40,
                    "humidity_max": 60,
                    "care_level": "easy",
                    "description": "Fast-growing vine that's perfect for beginners."
                },
                "peace_lily": {
                    "name": "Peace Lily",
                    "scientific_name": "Spathiphyllum",
                    "watering_interval": 5,
                    "humidity_min": 50,
                    "humidity_max": 70,
                    "care_level": "medium",
                    "description": "Elegant plant with white flowers that thrives in humid conditions."
                },
                "monstera": {
                    "name": "Monstera",
                    "scientific_name": "Monstera deliciosa",
                    "watering_interval": 7,
                    "humidity_min": 50,
                    "humidity_max": 70,
                    "care_level": "medium",
                    "description": "Popular plant with distinctive split leaves."
                },
                "zz_plant": {
                    "name": "ZZ Plant",
                    "scientific_name": "Zamioculcas zamiifolia",
                    "watering_interval": 14,
                    "humidity_min": 20,
                    "humidity_max": 40,
                    "care_level": "easy",
                    "description": "Extremely drought-tolerant plant with glossy leaves."
                }
            }
        }
    
    async def _save_database(self) -> None:
        """Save the database."""
        try:
            os.makedirs(os.path.dirname(self.database_file), exist_ok=True)
            async with aiofiles.open(self.database_file, 'w') as f:
                await f.write(json.dumps(self._data, indent=2))
        except Exception as err:
            _LOGGER.error(f"Failed to save plants database: {err}")
    
    def get_plant_info(self, plant_type: str) -> Optional[Dict[str, Any]]:
        """Get information about a plant type."""
        return self._data.get("plants", {}).get(plant_type)
    
    def get_all_plant_types(self) -> Dict[str, Any]:
        """Get all plant types."""
        return self._data.get("plants", {})
