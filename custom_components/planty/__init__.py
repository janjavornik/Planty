"""The Planty integration."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    CONF_PLANTS,
    SERVICE_WATER_PLANT,
    SERVICE_ADD_PLANT,
    SERVICE_REMOVE_PLANT,
    SERVICE_UPDATE_IMAGE,
)
from .image import async_setup_image_handler

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]

# Service schemas
WATER_PLANT_SCHEMA = vol.Schema({
    vol.Required("plant_id"): cv.string,
})

ADD_PLANT_SCHEMA = vol.Schema({
    vol.Required("plant_name"): cv.string,
    vol.Optional("plant_type"): cv.string,
    vol.Optional("watering_mode", default="manual"): vol.In(["sensor", "manual"]),
    vol.Optional("humidity_sensor"): cv.entity_id,
    vol.Optional("watering_interval", default=7): cv.positive_int,
})

UPDATE_IMAGE_SCHEMA = vol.Schema({
    vol.Required("plant_id"): cv.string,
    vol.Required("image_path"): cv.string,
})


class PlantyStorage:
    """Handle storage for Planty data."""
    
    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the storage handler."""
        self._store = Store(hass, 1, f"{DOMAIN}.storage")
        self._data: dict[str, Any] = {}
    
    async def async_load(self) -> dict[str, Any]:
        """Load data from storage."""
        stored_data = await self._store.async_load()
        if stored_data is None:
            stored_data = {"plants": {}}
        self._data = stored_data
        return self._data
    
    async def async_save(self) -> None:
        """Save data to storage."""
        await self._store.async_save(self._data)
    
    @property
    def data(self) -> dict[str, Any]:
        """Return the storage data."""
        return self._data


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Planty integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Planty from a config entry."""
    # Initialize storage
    storage = PlantyStorage(hass)
    await storage.async_load()
    
    # Load plant database
    plants_db = await async_load_plants_database(hass)
    
    # Set up image handler
    image_handler = await async_setup_image_handler(hass)
    
    # Store data in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "storage": storage,
        "plants_db": plants_db,
        "config": entry.data,
        "image_handler": image_handler,
    }
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services
    await async_register_services(hass, entry)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_load_plants_database(hass: HomeAssistant) -> dict[str, Any]:
    """Load the plants database from JSON file."""
    try:
        integration_path = os.path.dirname(__file__)
        plants_file = os.path.join(integration_path, "plants_data.json")
        
        def load_plants():
            with open(plants_file, encoding="utf-8") as f:
                return json.load(f)
        
        return await hass.async_add_executor_job(load_plants)
    except (FileNotFoundError, json.JSONDecodeError) as err:
        _LOGGER.error("Failed to load plants database: %s", err)
        return {"plants": {}}


async def async_register_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register Planty services."""
    
    async def water_plant_service(call: ServiceCall) -> None:
        """Handle water plant service call."""
        plant_id = call.data["plant_id"]
        storage = hass.data[DOMAIN][entry.entry_id]["storage"]
        
        # Update last watered time
        if "plants" not in storage.data:
            storage.data["plants"] = {}
        
        if plant_id not in storage.data["plants"]:
            storage.data["plants"][plant_id] = {}
        
        storage.data["plants"][plant_id]["last_watered"] = datetime.now().isoformat()
        await storage.async_save()
        
        # Fire event to update sensors
        hass.bus.async_fire(f"{DOMAIN}_plant_watered", {"plant_id": plant_id})
    
    async def add_plant_service(call: ServiceCall) -> None:
        """Handle add plant service call."""
        plant_name = call.data["plant_name"]
        plant_type = call.data.get("plant_type")
        watering_mode = call.data["watering_mode"]
        humidity_sensor = call.data.get("humidity_sensor")
        watering_interval = call.data["watering_interval"]
        
        storage = hass.data[DOMAIN][entry.entry_id]["storage"]
        
        if "plants" not in storage.data:
            storage.data["plants"] = {}
        
        plant_id = plant_name.lower().replace(" ", "_")
        storage.data["plants"][plant_id] = {
            "name": plant_name,
            "type": plant_type,
            "watering_mode": watering_mode,
            "humidity_sensor": humidity_sensor,
            "watering_interval": watering_interval,
            "created": datetime.now().isoformat(),
        }
        
        await storage.async_save()
        
        # Reload the integration to create new entities
        await hass.config_entries.async_reload(entry.entry_id)
    
    async def update_image_service(call: ServiceCall) -> None:
        """Handle update plant image service call."""
        plant_id = call.data["plant_id"]
        image_path = call.data["image_path"]
        
        storage = hass.data[DOMAIN][entry.entry_id]["storage"]
        
        if "plants" in storage.data and plant_id in storage.data["plants"]:
            storage.data["plants"][plant_id]["image_path"] = image_path
            await storage.async_save()
            
            # Fire event to update entities
            hass.bus.async_fire(f"{DOMAIN}_plant_updated", {"plant_id": plant_id})
    
    # Register services
    hass.services.async_register(
        DOMAIN, SERVICE_WATER_PLANT, water_plant_service, schema=WATER_PLANT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_PLANT, add_plant_service, schema=ADD_PLANT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_IMAGE, update_image_service, schema=UPDATE_IMAGE_SCHEMA
    )


def get_plant_data(hass: HomeAssistant, entry_id: str, plant_id: str) -> dict[str, Any] | None:
    """Get plant data from storage."""
    storage = hass.data[DOMAIN][entry_id]["storage"]
    return storage.data.get("plants", {}).get(plant_id)


def get_plant_database(hass: HomeAssistant, entry_id: str) -> dict[str, Any]:
    """Get the plants database."""
    return hass.data[DOMAIN][entry_id]["plants_db"]
