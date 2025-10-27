"""Dashboard management for Planty integration."""
from __future__ import annotations

import logging
import yaml
from typing import Any, Dict

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.storage import Store
from homeassistant.components import frontend

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DASHBOARD_URL_PATH = "my-plants"
DASHBOARD_TITLE = "My Plants"
DASHBOARD_ICON = "mdi:leaf"


class DashboardManager:
    """Manage the My Plants dashboard."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the dashboard manager."""
        self.hass = hass
        self.entry = entry
        self._store = Store(hass, 1, f"{DOMAIN}_dashboard")
    
    async def async_create_dashboard(self) -> None:
        """Create and register the My Plants dashboard."""
        try:
            # Generate dashboard configuration
            dashboard_config = await self._generate_dashboard_config()
            
            # Register the dashboard
            await self._register_dashboard(dashboard_config)
            
            _LOGGER.info("Successfully created My Plants dashboard")
            
        except Exception as err:
            _LOGGER.error("Failed to create My Plants dashboard: %s", err)
    
    async def async_update_dashboard(self) -> None:
        """Update the dashboard with current plants."""
        try:
            dashboard_config = await self._generate_dashboard_config()
            await self._register_dashboard(dashboard_config)
            _LOGGER.debug("Updated My Plants dashboard")
        except Exception as err:
            _LOGGER.error("Failed to update dashboard: %s", err)
    
    async def async_remove_dashboard(self) -> None:
        """Remove the My Plants dashboard."""
        try:
            # Remove from lovelace config if it exists
            if hasattr(self.hass.data, "lovelace"):
                lovelace_config = self.hass.data.get("lovelace", {})
                if DASHBOARD_URL_PATH in lovelace_config.get("dashboards", {}):
                    del lovelace_config["dashboards"][DASHBOARD_URL_PATH]
            
            _LOGGER.info("Removed My Plants dashboard")
        except Exception as err:
            _LOGGER.error("Failed to remove dashboard: %s", err)
    
    async def _generate_dashboard_config(self) -> Dict[str, Any]:
        """Generate dashboard configuration based on current plants."""
        storage = self.hass.data[DOMAIN][self.entry.entry_id]["storage"]
        plants = storage.data.get("plants", {})
        
        # Generate cards for each plant
        cards = []
        
        # Add header card
        cards.append({
            "type": "custom:planty-header-card",
            "title": "My Plants",
            "subtitle": f"{len(plants)} plants tracked"
        })
        
        # Add settings card
        cards.append({
            "type": "custom:planty-settings-card"
        })
        
        # Add plant cards
        for plant_id, plant_config in plants.items():
            plant_name = plant_config.get("name", plant_id)
            plant_type = plant_config.get("type", "custom")
            watering_mode = plant_config.get("watering_mode", "manual")
            
            card_config = {
                "type": "custom:planty-card",
                "entity": f"sensor.planty_{plant_id}_water_status",
                "plant_id": plant_id,
                "name": plant_name,
                "plant_type": plant_type,
                "watering_mode": watering_mode,
                "image": plant_config.get("image_path"),
                "humidity_sensor": plant_config.get("humidity_sensor"),
                "watering_interval": plant_config.get("watering_interval", 7)
            }
            
            cards.append(card_config)
        
        # If no plants, show welcome card
        if not plants:
            cards.append({
                "type": "custom:planty-welcome-card"
            })
        
        return {
            "title": DASHBOARD_TITLE,
            "path": DASHBOARD_URL_PATH,
            "icon": DASHBOARD_ICON,
            "show_in_sidebar": True,
            "cards": cards
        }
    
    async def _register_dashboard(self, dashboard_config: Dict[str, Any]) -> None:
        """Register the dashboard with Home Assistant."""
        # Store dashboard config
        await self._store.async_save(dashboard_config)
        
        try:
            # Try to use the lovelace integration's dashboard registration
            from homeassistant.components.lovelace import dashboard
            
            # Create dashboard
            dashboard_obj = dashboard.LovelaceDashboard(
                self.hass,
                DASHBOARD_URL_PATH,
                {
                    "mode": "yaml",
                    "title": DASHBOARD_TITLE,
                    "icon": DASHBOARD_ICON,
                    "show_in_sidebar": True,
                    "require_admin": False,
                    "config": dashboard_config
                }
            )
            
            # Register with hass
            if "lovelace" not in self.hass.data:
                self.hass.data["lovelace"] = {}
            if "dashboards" not in self.hass.data["lovelace"]:
                self.hass.data["lovelace"]["dashboards"] = {}
            
            self.hass.data["lovelace"]["dashboards"][DASHBOARD_URL_PATH] = dashboard_obj
            
        except ImportError:
            # Fallback registration method
            _LOGGER.warning("Could not import lovelace dashboard, using fallback registration")
            
            # Register with frontend
            await self._register_with_frontend(dashboard_config)
        
        # Fire event to update frontend
        self.hass.bus.async_fire("lovelace_updated", {
            "url_path": DASHBOARD_URL_PATH,
            "mode": "yaml"
        })
    
    async def _register_with_frontend(self, dashboard_config: Dict[str, Any]) -> None:
        """Fallback method to register dashboard with frontend."""
        try:
            from homeassistant.components import frontend
            
            # Register the dashboard URL
            frontend.async_register_built_in_panel(
                self.hass,
                "lovelace",
                DASHBOARD_TITLE,
                DASHBOARD_ICON,
                DASHBOARD_URL_PATH,
                {"mode": "yaml"},
                require_admin=False,
                sidebar_title=DASHBOARD_TITLE,
                sidebar_icon=DASHBOARD_ICON,
                url_path=DASHBOARD_URL_PATH
            )
            
        except Exception as err:
            _LOGGER.error("Failed to register dashboard with frontend: %s", err)


async def async_setup_dashboard(hass: HomeAssistant, entry: ConfigEntry) -> DashboardManager:
    """Set up the dashboard manager."""
    manager = DashboardManager(hass, entry)
    await manager.async_create_dashboard()
    return manager
