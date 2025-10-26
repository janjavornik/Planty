"""Plant management logic for Planty."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .ha_client import HomeAssistantClient
from .storage import PlantyStorage, PlantsDatabase

_LOGGER = logging.getLogger(__name__)

# Plant status constants
PLANT_STATUS_HEALTHY = "healthy"
PLANT_STATUS_NEEDS_WATER = "needs_water"
PLANT_STATUS_OVERDUE = "overdue"
PLANT_STATUS_UNKNOWN = "unknown"


class PlantManager:
    """Manage plants and their states."""
    
    def __init__(self, storage: PlantyStorage, plants_db: PlantsDatabase) -> None:
        """Initialize the plant manager."""
        self.storage = storage
        self.plants_db = plants_db
        self._update_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the plant manager."""
        _LOGGER.info("Starting plant manager...")
        
        # Load data
        await self.storage.load()
        await self.plants_db.load()
        
        # Start update task
        self._update_task = asyncio.create_task(self._update_loop())
    
    async def stop(self) -> None:
        """Stop the plant manager."""
        _LOGGER.info("Stopping plant manager...")
        
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
    
    async def _update_loop(self) -> None:
        """Main update loop."""
        while True:
            try:
                await self._update_plant_states()
                await asyncio.sleep(300)  # Update every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as err:
                _LOGGER.error(f"Error in update loop: {err}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _update_plant_states(self) -> None:
        """Update plant states in Home Assistant."""
        async with HomeAssistantClient() as ha_client:
            plants = self.storage.get_all_plants()
            
            for plant_id, plant_data in plants.items():
                try:
                    await self._update_single_plant(ha_client, plant_id, plant_data)
                except Exception as err:
                    _LOGGER.error(f"Error updating plant {plant_id}: {err}")
    
    async def _update_single_plant(self, ha_client: HomeAssistantClient, 
                                 plant_id: str, plant_data: Dict[str, Any]) -> None:
        """Update a single plant's state."""
        plant_name = plant_data.get("name", plant_id)
        
        # Calculate days until watering
        days_until_water = self._calculate_days_until_water(plant_data)
        
        # Get water status
        water_status = await self._get_water_status(ha_client, plant_data)
        
        # Get humidity if using sensor mode
        humidity = None
        if plant_data.get("watering_mode") == "sensor":
            humidity = await self._get_humidity(ha_client, plant_data)
        
        # Update sensors
        await self._update_sensors(ha_client, plant_id, plant_name, {
            "days_until_water": days_until_water,
            "water_status": water_status,
            "humidity": humidity,
            "last_watered": plant_data.get("last_watered"),
            "plant_data": plant_data
        })
    
    def _calculate_days_until_water(self, plant_data: Dict[str, Any]) -> int:
        """Calculate days until next watering."""
        last_watered_str = plant_data.get("last_watered")
        if not last_watered_str:
            return 0
        
        try:
            last_watered = datetime.fromisoformat(last_watered_str)
            watering_interval = plant_data.get("watering_interval", 7)
            next_watering = last_watered + timedelta(days=watering_interval)
            days_until = (next_watering - datetime.now()).days
            return max(0, days_until)
        except (ValueError, TypeError):
            return 0
    
    async def _get_water_status(self, ha_client: HomeAssistantClient, 
                              plant_data: Dict[str, Any]) -> str:
        """Get the plant's water status."""
        if plant_data.get("watering_mode") == "sensor":
            return await self._get_sensor_status(ha_client, plant_data)
        else:
            return self._get_manual_status(plant_data)
    
    async def _get_sensor_status(self, ha_client: HomeAssistantClient, 
                               plant_data: Dict[str, Any]) -> str:
        """Get status based on humidity sensor."""
        humidity_sensor = plant_data.get("humidity_sensor")
        if not humidity_sensor:
            return PLANT_STATUS_UNKNOWN
        
        sensor_state = await ha_client.get_state(humidity_sensor)
        if not sensor_state or sensor_state.get("state") == "unavailable":
            return PLANT_STATUS_UNKNOWN
        
        try:
            current_humidity = float(sensor_state["state"])
            
            # Get plant type data
            plant_type = plant_data.get("type")
            plant_info = self.plants_db.get_plant_info(plant_type) if plant_type else None
            
            if plant_info:
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
    
    def _get_manual_status(self, plant_data: Dict[str, Any]) -> str:
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
    
    async def _get_humidity(self, ha_client: HomeAssistantClient, 
                          plant_data: Dict[str, Any]) -> Optional[float]:
        """Get humidity from sensor."""
        humidity_sensor = plant_data.get("humidity_sensor")
        if not humidity_sensor:
            return None
        
        sensor_state = await ha_client.get_state(humidity_sensor)
        if not sensor_state or sensor_state.get("state") == "unavailable":
            return None
        
        try:
            return float(sensor_state["state"])
        except (ValueError, TypeError):
            return None
    
    async def _update_sensors(self, ha_client: HomeAssistantClient, 
                            plant_id: str, plant_name: str, 
                            data: Dict[str, Any]) -> None:
        """Update sensors in Home Assistant."""
        # Days until water sensor
        if data["days_until_water"] is not None:
            await ha_client.create_sensor(
                f"sensor.planty_{plant_id}_days_until_water",
                f"{plant_name} Days Until Watering",
                str(data["days_until_water"]),
                attributes={
                    "watering_interval": data["plant_data"].get("watering_interval", 7),
                    "watering_mode": data["plant_data"].get("watering_mode", "manual"),
                    "plant_type": data["plant_data"].get("type"),
                },
                unit_of_measurement="days",
                icon="mdi:calendar-clock"
            )
        
        # Water status sensor
        await ha_client.create_sensor(
            f"sensor.planty_{plant_id}_water_status",
            f"{plant_name} Water Status",
            data["water_status"],
            attributes={
                "friendly_name": f"{plant_name} Water Status",
                "plant_id": plant_id,
            },
            icon=self._get_status_icon(data["water_status"])
        )
        
        # Last watered sensor
        if data["last_watered"]:
            await ha_client.create_sensor(
                f"sensor.planty_{plant_id}_last_watered",
                f"{plant_name} Last Watered",
                data["last_watered"],
                device_class="timestamp",
                icon="mdi:calendar-check"
            )
        
        # Humidity sensor (if available)
        if data["humidity"] is not None:
            await ha_client.create_sensor(
                f"sensor.planty_{plant_id}_humidity",
                f"{plant_name} Soil Humidity",
                str(data["humidity"]),
                attributes={
                    "source_sensor": data["plant_data"].get("humidity_sensor"),
                },
                unit_of_measurement="%",
                device_class="humidity",
                icon="mdi:water-percent"
            )
    
    def _get_status_icon(self, status: str) -> str:
        """Get icon based on status."""
        if status == PLANT_STATUS_HEALTHY:
            return "mdi:water-check"
        elif status == PLANT_STATUS_NEEDS_WATER:
            return "mdi:water-alert"
        elif status == PLANT_STATUS_OVERDUE:
            return "mdi:water-off"
        else:
            return "mdi:water-unknown"
    
    # Public API methods
    async def add_plant(self, plant_data: Dict[str, Any]) -> str:
        """Add a new plant."""
        plant_name = plant_data["plant_name"]
        plant_id = plant_name.lower().replace(" ", "_").replace("-", "_")
        
        # Ensure unique ID
        counter = 1
        original_id = plant_id
        while self.storage.get_plant(plant_id):
            plant_id = f"{original_id}_{counter}"
            counter += 1
        
        await self.storage.add_plant(plant_id, {
            "name": plant_name,
            "type": plant_data.get("plant_type"),
            "watering_mode": plant_data.get("watering_mode", "manual"),
            "humidity_sensor": plant_data.get("humidity_sensor"),
            "watering_interval": plant_data.get("watering_interval", 7),
            "image_path": plant_data.get("image_path"),
        })
        
        return plant_id
    
    async def water_plant(self, plant_id: str) -> bool:
        """Water a plant."""
        success = await self.storage.water_plant(plant_id)
        if success:
            # Fire event
            async with HomeAssistantClient() as ha_client:
                await ha_client.fire_event("planty_plant_watered", {"plant_id": plant_id})
        return success
    
    async def remove_plant(self, plant_id: str) -> bool:
        """Remove a plant."""
        return await self.storage.remove_plant(plant_id)
    
    async def update_plant(self, plant_id: str, updates: Dict[str, Any]) -> bool:
        """Update a plant."""
        return await self.storage.update_plant(plant_id, updates)
    
    def get_plant(self, plant_id: str) -> Optional[Dict[str, Any]]:
        """Get a plant."""
        return self.storage.get_plant(plant_id)
    
    def get_all_plants(self) -> Dict[str, Any]:
        """Get all plants."""
        return self.storage.get_all_plants()
    
    def get_plant_types(self) -> Dict[str, Any]:
        """Get all available plant types."""
        return self.plants_db.get_all_plant_types()
