"""Plant sensors for Planty integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from . import get_plant_data, get_plant_database
from .const import (
    DOMAIN,
    SENSOR_TYPES,
    PLANT_STATUS_HEALTHY,
    PLANT_STATUS_NEEDS_WATER,
    PLANT_STATUS_OVERDUE,
    PLANT_STATUS_UNKNOWN,
    WATERING_MODE_SENSOR,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Planty sensors from a config entry."""
    storage = hass.data[DOMAIN][config_entry.entry_id]["storage"]
    plants_db = hass.data[DOMAIN][config_entry.entry_id]["plants_db"]
    
    entities = []
    
    # Create sensors for each plant
    for plant_id, plant_config in storage.data.get("plants", {}).items():
        # Create basic sensors for all plants
        entities.extend([
            PlantDaysUntilWaterSensor(hass, config_entry, plant_id, plant_config),
            PlantLastWateredSensor(hass, config_entry, plant_id, plant_config),
            PlantWaterStatusSensor(hass, config_entry, plant_id, plant_config),
        ])
        
        # Create humidity sensor if plant uses sensor mode
        if plant_config.get("watering_mode") == WATERING_MODE_SENSOR:
            entities.append(
                PlantHumiditySensor(hass, config_entry, plant_id, plant_config)
            )
    
    async_add_entities(entities)


class PlantSensorBase(SensorEntity):
    """Base class for plant sensors."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        config_entry: ConfigEntry, 
        plant_id: str, 
        plant_config: dict[str, Any],
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._config_entry = config_entry
        self._plant_id = plant_id
        self._plant_config = plant_config
        self._sensor_type = sensor_type
        
        sensor_info = SENSOR_TYPES[sensor_type]
        plant_name = plant_config.get("name", plant_id)
        
        self._attr_name = f"{plant_name} {sensor_info['name']}"
        self._attr_unique_id = f"{DOMAIN}_{plant_id}_{sensor_type}"
        self._attr_icon = sensor_info["icon"]
        self._attr_native_unit_of_measurement = sensor_info.get("unit")
        self._attr_device_class = sensor_info.get("device_class")
        
        # Set up device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, plant_id)},
            name=plant_name,
            manufacturer="Planty",
            model=plant_config.get("type", "Custom Plant"),
            sw_version="1.0.0",
        )

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        # Listen for plant events
        self.async_on_remove(
            self.hass.bus.async_listen(
                f"{DOMAIN}_plant_watered",
                self._handle_plant_event,
            )
        )
        self.async_on_remove(
            self.hass.bus.async_listen(
                f"{DOMAIN}_plant_updated",
                self._handle_plant_event,
            )
        )

    @callback
    def _handle_plant_event(self, event) -> None:
        """Handle plant events."""
        if event.data.get("plant_id") == self._plant_id:
            self.async_schedule_update_ha_state()


class PlantDaysUntilWaterSensor(PlantSensorBase):
    """Sensor for days until next watering."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        config_entry: ConfigEntry, 
        plant_id: str, 
        plant_config: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(hass, config_entry, plant_id, plant_config, "days_until_water")
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the number of days until next watering."""
        plant_data = get_plant_data(self.hass, self._config_entry.entry_id, self._plant_id)
        if not plant_data:
            return None

        last_watered_str = plant_data.get("last_watered")
        if not last_watered_str:
            return 0  # Needs to be watered immediately

        try:
            last_watered = datetime.fromisoformat(last_watered_str)
            watering_interval = plant_data.get("watering_interval", 7)
            next_watering = last_watered + timedelta(days=watering_interval)
            days_until = (next_watering - datetime.now()).days
            return max(0, days_until)
        except (ValueError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        plant_data = get_plant_data(self.hass, self._config_entry.entry_id, self._plant_id)
        if not plant_data:
            return {}

        attrs = {
            "watering_interval": plant_data.get("watering_interval", 7),
            "watering_mode": plant_data.get("watering_mode", "manual"),
            "progress_percentage": self._calculate_progress_percentage(),
            "color_state": self._get_color_state(),
        }

        last_watered_str = plant_data.get("last_watered")
        if last_watered_str:
            try:
                last_watered = datetime.fromisoformat(last_watered_str)
                watering_interval = plant_data.get("watering_interval", 7)
                next_watering = last_watered + timedelta(days=watering_interval)
                attrs["next_watering"] = next_watering.isoformat()
            except (ValueError, TypeError):
                pass

        return attrs
    
    def _calculate_progress_percentage(self) -> int:
        """Calculate progress percentage for progress bar."""
        plant_data = get_plant_data(self.hass, self._config_entry.entry_id, self._plant_id)
        if not plant_data:
            return 0

        last_watered_str = plant_data.get("last_watered")
        if not last_watered_str:
            return 100  # Needs water immediately

        try:
            last_watered = datetime.fromisoformat(last_watered_str)
            watering_interval = plant_data.get("watering_interval", 7)
            days_passed = (datetime.now() - last_watered).days
            
            # Calculate percentage (0% = just watered, 100% = needs water)
            percentage = min(100, max(0, (days_passed / watering_interval) * 100))
            return int(percentage)
        except (ValueError, TypeError):
            return 0
    
    def _get_color_state(self) -> str:
        """Get color state for the progress bar."""
        progress = self._calculate_progress_percentage()
        
        if progress >= 100:
            return "red"  # Needs water now
        elif progress >= 80:
            return "orange"  # Watering soon
        else:
            return "green"  # Happy camper


class PlantLastWateredSensor(PlantSensorBase):
    """Sensor for when the plant was last watered."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        config_entry: ConfigEntry, 
        plant_id: str, 
        plant_config: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(hass, config_entry, plant_id, plant_config, "last_watered")

    @property
    def native_value(self) -> datetime | None:
        """Return when the plant was last watered."""
        plant_data = get_plant_data(self.hass, self._config_entry.entry_id, self._plant_id)
        if not plant_data:
            return None

        last_watered_str = plant_data.get("last_watered")
        if not last_watered_str:
            return None

        try:
            return datetime.fromisoformat(last_watered_str)
        except (ValueError, TypeError):
            return None


class PlantWaterStatusSensor(PlantSensorBase):
    """Sensor for plant watering status."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        config_entry: ConfigEntry, 
        plant_id: str, 
        plant_config: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(hass, config_entry, plant_id, plant_config, "water_status")

    @property
    def native_value(self) -> str:
        """Return the plant's water status."""
        plant_data = get_plant_data(self.hass, self._config_entry.entry_id, self._plant_id)
        if not plant_data:
            return PLANT_STATUS_UNKNOWN

        # Check if using sensor mode
        if plant_data.get("watering_mode") == WATERING_MODE_SENSOR:
            return self._get_sensor_status(plant_data)
        else:
            return self._get_manual_status(plant_data)

    def _get_sensor_status(self, plant_data: dict[str, Any]) -> str:
        """Get status based on humidity sensor."""
        humidity_sensor = plant_data.get("humidity_sensor")
        if not humidity_sensor:
            return PLANT_STATUS_UNKNOWN

        humidity_state = self.hass.states.get(humidity_sensor)
        if not humidity_state or humidity_state.state == "unavailable":
            return PLANT_STATUS_UNKNOWN

        try:
            current_humidity = float(humidity_state.state)
            
            # Get plant type data if available
            plants_db = get_plant_database(self.hass, self._config_entry.entry_id)
            plant_type = plant_data.get("type")
            
            if plant_type and plant_type in plants_db.get("plants", {}):
                plant_info = plants_db["plants"][plant_type]
                humidity_min = plant_info.get("humidity_min", 30)
                humidity_max = plant_info.get("humidity_max", 70)
            else:
                humidity_min = 30
                humidity_max = 70

            if current_humidity < humidity_min:
                return PLANT_STATUS_NEEDS_WATER
            elif current_humidity > humidity_max:
                return PLANT_STATUS_OVERDUE  # Too wet
            else:
                return PLANT_STATUS_HEALTHY

        except (ValueError, TypeError):
            return PLANT_STATUS_UNKNOWN

    def _get_manual_status(self, plant_data: dict[str, Any]) -> str:
        """Get status based on manual countdown."""
        last_watered_str = plant_data.get("last_watered")
        if not last_watered_str:
            return PLANT_STATUS_NEEDS_WATER

        try:
            last_watered = datetime.fromisoformat(last_watered_str)
            watering_interval = plant_data.get("watering_interval", 7)
            next_watering = last_watered + timedelta(days=watering_interval)
            now = datetime.now()

            if now > next_watering + timedelta(days=2):  # 2 days overdue
                return PLANT_STATUS_OVERDUE
            elif now >= next_watering:
                return PLANT_STATUS_NEEDS_WATER
            else:
                return PLANT_STATUS_HEALTHY

        except (ValueError, TypeError):
            return PLANT_STATUS_UNKNOWN

    @property
    def icon(self) -> str:
        """Return the icon based on status."""
        status = self.native_value
        if status == PLANT_STATUS_HEALTHY:
            return "mdi:water-check"
        elif status == PLANT_STATUS_NEEDS_WATER:
            return "mdi:water-alert"
        elif status == PLANT_STATUS_OVERDUE:
            return "mdi:water-off"
        else:
            return "mdi:water-unknown"
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        plant_data = get_plant_data(self.hass, self._config_entry.entry_id, self._plant_id)
        if not plant_data:
            return {}

        attrs = {
            "plant_id": self._plant_id,
            "watering_mode": plant_data.get("watering_mode", "manual"),
            "progress_percentage": self._calculate_progress_percentage(),
            "color_state": self._get_color_state(),
        }

        # Add sensor-specific attributes
        if plant_data.get("watering_mode") == WATERING_MODE_SENSOR:
            humidity_sensor = plant_data.get("humidity_sensor")
            if humidity_sensor:
                humidity_state = self.hass.states.get(humidity_sensor)
                if humidity_state and humidity_state.state != "unavailable":
                    try:
                        attrs["current_humidity"] = float(humidity_state.state)
                    except (ValueError, TypeError):
                        pass
                attrs["humidity_sensor"] = humidity_sensor
        else:
            # Manual mode attributes
            attrs["watering_interval"] = plant_data.get("watering_interval", 7)
            last_watered_str = plant_data.get("last_watered")
            if last_watered_str:
                try:
                    last_watered = datetime.fromisoformat(last_watered_str)
                    days_since_watered = (datetime.now() - last_watered).days
                    attrs["days_since_watered"] = days_since_watered
                except (ValueError, TypeError):
                    pass

        return attrs
    
    def _calculate_progress_percentage(self) -> int:
        """Calculate progress percentage for progress bar."""
        plant_data = get_plant_data(self.hass, self._config_entry.entry_id, self._plant_id)
        if not plant_data:
            return 0

        if plant_data.get("watering_mode") == WATERING_MODE_SENSOR:
            return self._calculate_sensor_progress(plant_data)
        else:
            return self._calculate_manual_progress(plant_data)
    
    def _calculate_sensor_progress(self, plant_data: dict[str, Any]) -> int:
        """Calculate progress for sensor mode."""
        humidity_sensor = plant_data.get("humidity_sensor")
        if not humidity_sensor:
            return 0

        humidity_state = self.hass.states.get(humidity_sensor)
        if not humidity_state or humidity_state.state == "unavailable":
            return 0

        try:
            current_humidity = float(humidity_state.state)
            
            # Get plant type thresholds
            plants_db = get_plant_database(self.hass, self._config_entry.entry_id)
            plant_type = plant_data.get("type")
            
            if plant_type and plant_type in plants_db.get("plants", {}):
                plant_info = plants_db["plants"][plant_type]
                humidity_min = plant_info.get("humidity_min", 30)
                humidity_max = plant_info.get("humidity_max", 70)
            else:
                humidity_min = 30
                humidity_max = 70
            
            # Calculate inverse percentage (lower humidity = higher progress)
            optimal_range = humidity_max - humidity_min
            if current_humidity >= humidity_max:
                return 0  # Too wet, no watering needed
            elif current_humidity <= humidity_min:
                return 100  # Needs water
            else:
                # Linear scale from optimal to needs water
                progress = ((humidity_max - current_humidity) / optimal_range) * 100
                return int(min(100, max(0, progress)))
                
        except (ValueError, TypeError):
            return 0
    
    def _calculate_manual_progress(self, plant_data: dict[str, Any]) -> int:
        """Calculate progress for manual mode."""
        last_watered_str = plant_data.get("last_watered")
        if not last_watered_str:
            return 100  # Needs water immediately

        try:
            last_watered = datetime.fromisoformat(last_watered_str)
            watering_interval = plant_data.get("watering_interval", 7)
            days_passed = (datetime.now() - last_watered).days
            
            # Calculate percentage (0% = just watered, 100% = needs water)
            percentage = min(100, max(0, (days_passed / watering_interval) * 100))
            return int(percentage)
        except (ValueError, TypeError):
            return 0
    
    def _get_color_state(self) -> str:
        """Get color state for the progress bar."""
        progress = self._calculate_progress_percentage()
        
        if progress >= 100:
            return "red"  # Needs water now
        elif progress >= 80:
            return "orange"  # Watering soon
        else:
            return "green"  # Happy camper


class PlantHumiditySensor(PlantSensorBase):
    """Sensor for plant soil humidity (proxy sensor)."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        config_entry: ConfigEntry, 
        plant_id: str, 
        plant_config: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(hass, config_entry, plant_id, plant_config, "humidity")
        self._attr_state_class = SensorStateClass.MEASUREMENT
        
        # Track the source humidity sensor
        self._source_sensor = plant_config.get("humidity_sensor")

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Track source sensor state changes
        if self._source_sensor:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    [self._source_sensor],
                    self._source_sensor_changed,
                )
            )

    @callback
    def _source_sensor_changed(self, event) -> None:
        """Handle source sensor state change."""
        self.async_schedule_update_ha_state()

    @property
    def native_value(self) -> float | None:
        """Return the current humidity from the source sensor."""
        if not self._source_sensor:
            return None

        source_state = self.hass.states.get(self._source_sensor)
        if not source_state or source_state.state == "unavailable":
            return None

        try:
            return float(source_state.state)
        except (ValueError, TypeError):
            return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not self._source_sensor:
            return False

        source_state = self.hass.states.get(self._source_sensor)
        return source_state is not None and source_state.state != "unavailable"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {"source_sensor": self._source_sensor}
        
        # Get plant type data if available
        plants_db = get_plant_database(self.hass, self._config_entry.entry_id)
        plant_type = self._plant_config.get("type")
        
        if plant_type and plant_type in plants_db.get("plants", {}):
            plant_info = plants_db["plants"][plant_type]
            attrs.update({
                "humidity_min": plant_info.get("humidity_min", 30),
                "humidity_max": plant_info.get("humidity_max", 70),
                "plant_type": plant_type,
            })

        return attrs
