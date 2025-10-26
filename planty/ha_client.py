"""Home Assistant API client for Planty."""
from __future__ import annotations

import aiohttp
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from .config import config

_LOGGER = logging.getLogger(__name__)


class HomeAssistantClient:
    """Client for communicating with Home Assistant API."""
    
    def __init__(self) -> None:
        """Initialize the client."""
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = config.homeassistant_url
        self.headers = config.headers
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=self.headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get state of an entity."""
        if not self.session:
            return None
        
        try:
            url = f"{self.base_url}/api/states/{entity_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOGGER.warning(f"Failed to get state for {entity_id}: {response.status}")
                    return None
        except Exception as err:
            _LOGGER.error(f"Error getting state for {entity_id}: {err}")
            return None
    
    async def set_state(self, entity_id: str, state: str, attributes: Optional[Dict[str, Any]] = None) -> bool:
        """Set state of an entity."""
        if not self.session:
            return False
        
        try:
            url = f"{self.base_url}/api/states/{entity_id}"
            data = {
                "state": state,
                "attributes": attributes or {}
            }
            async with self.session.post(url, json=data) as response:
                return response.status in [200, 201]
        except Exception as err:
            _LOGGER.error(f"Error setting state for {entity_id}: {err}")
            return False
    
    async def call_service(self, domain: str, service: str, service_data: Optional[Dict[str, Any]] = None) -> bool:
        """Call a Home Assistant service."""
        if not self.session:
            return False
        
        try:
            url = f"{self.base_url}/api/services/{domain}/{service}"
            async with self.session.post(url, json=service_data or {}) as response:
                return response.status == 200
        except Exception as err:
            _LOGGER.error(f"Error calling service {domain}.{service}: {err}")
            return False
    
    async def get_entities(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all entities or entities from a specific domain."""
        if not self.session:
            return []
        
        try:
            url = f"{self.base_url}/api/states"
            async with self.session.get(url) as response:
                if response.status == 200:
                    entities = await response.json()
                    if domain:
                        return [e for e in entities if e["entity_id"].startswith(f"{domain}.")]
                    return entities
                else:
                    _LOGGER.warning(f"Failed to get entities: {response.status}")
                    return []
        except Exception as err:
            _LOGGER.error(f"Error getting entities: {err}")
            return []
    
    async def create_sensor(self, entity_id: str, name: str, state: str, 
                          attributes: Optional[Dict[str, Any]] = None, 
                          device_class: Optional[str] = None,
                          unit_of_measurement: Optional[str] = None,
                          icon: Optional[str] = None) -> bool:
        """Create a sensor entity in Home Assistant."""
        sensor_attributes = {
            "friendly_name": name,
            "device_class": device_class,
            "unit_of_measurement": unit_of_measurement,
            "icon": icon,
        }
        
        # Remove None values
        sensor_attributes = {k: v for k, v in sensor_attributes.items() if v is not None}
        
        # Add custom attributes
        if attributes:
            sensor_attributes.update(attributes)
        
        return await self.set_state(entity_id, state, sensor_attributes)
    
    async def fire_event(self, event_type: str, event_data: Optional[Dict[str, Any]] = None) -> bool:
        """Fire an event in Home Assistant."""
        if not self.session:
            return False
        
        try:
            url = f"{self.base_url}/api/events/{event_type}"
            async with self.session.post(url, json=event_data or {}) as response:
                return response.status == 200
        except Exception as err:
            _LOGGER.error(f"Error firing event {event_type}: {err}")
            return False
    
    async def get_config(self) -> Optional[Dict[str, Any]]:
        """Get Home Assistant configuration."""
        if not self.session:
            return None
        
        try:
            url = f"{self.base_url}/api/config"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOGGER.warning(f"Failed to get config: {response.status}")
                    return None
        except Exception as err:
            _LOGGER.error(f"Error getting config: {err}")
            return None
