"""Button entities for Planty integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import get_plant_data
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Planty button entities from a config entry."""
    storage = hass.data[DOMAIN][config_entry.entry_id]["storage"]
    
    entities = []
    
    # Create water button for each plant
    for plant_id, plant_config in storage.data.get("plants", {}).items():
        entities.append(PlantWaterButton(hass, config_entry, plant_id, plant_config))
    
    async_add_entities(entities)


class PlantWaterButton(ButtonEntity):
    """Button to water a plant."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        plant_id: str,
        plant_config: dict[str, Any],
    ) -> None:
        """Initialize the button."""
        self.hass = hass
        self._config_entry = config_entry
        self._plant_id = plant_id
        self._plant_config = plant_config
        
        plant_name = plant_config.get("name", plant_id)
        
        self._attr_name = f"{plant_name} Water"
        self._attr_unique_id = f"{DOMAIN}_{plant_id}_water_button"
        self._attr_icon = "mdi:water"
        
        # Set up device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, plant_id)},
            name=plant_name,
            manufacturer="Planty",
            model=plant_config.get("type", "Custom Plant"),
            sw_version="1.0.0",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        storage = self.hass.data[DOMAIN][self._config_entry.entry_id]["storage"]
        
        # Update last watered time
        if "plants" not in storage.data:
            storage.data["plants"] = {}
        
        if self._plant_id not in storage.data["plants"]:
            storage.data["plants"][self._plant_id] = {}
        
        storage.data["plants"][self._plant_id]["last_watered"] = datetime.now().isoformat()
        await storage.async_save()
        
        # Fire event to update sensors
        self.hass.bus.async_fire(f"{DOMAIN}_plant_watered", {"plant_id": self._plant_id})
        
        _LOGGER.info("Plant %s was watered", self._plant_config.get("name", self._plant_id))
