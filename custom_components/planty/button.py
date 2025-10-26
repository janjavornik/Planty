"""Plant buttons for Planty integration."""
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
    """Set up Planty buttons from a config entry."""
    storage = hass.data[DOMAIN][config_entry.entry_id]["storage"]
    
    entities = []
    
    # Create water button for each plant
    for plant_id, plant_config in storage.data.get("plants", {}).items():
        entities.append(PlantWaterButton(hass, config_entry, plant_id, plant_config))
    
    async_add_entities(entities)


class PlantWaterButton(ButtonEntity):
    """Button to water a plant manually."""

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
        self._attr_icon = "mdi:watering-can"
        
        # Set up device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, plant_id)},
            name=plant_name,
            manufacturer="Planty",
            model=plant_config.get("type", "Custom Plant"),
            sw_version="1.0.0",
        )

    async def async_press(self) -> None:
        """Handle button press."""
        # Call the water plant service
        await self.hass.services.async_call(
            DOMAIN,
            "water_plant",
            {"plant_id": self._plant_id},
            blocking=True,
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        plant_data = get_plant_data(self.hass, self._config_entry.entry_id, self._plant_id)
        if not plant_data:
            return {}

        attrs = {
            "plant_id": self._plant_id,
            "watering_mode": plant_data.get("watering_mode", "manual"),
            "watering_interval": plant_data.get("watering_interval", 7),
        }

        last_watered_str = plant_data.get("last_watered")
        if last_watered_str:
            attrs["last_watered"] = last_watered_str

        return attrs
