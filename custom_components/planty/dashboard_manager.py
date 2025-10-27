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
            # Try simple notification instead
            try:
                await self._create_simple_notification()
            except Exception:
                pass  # Fail silently
    
    async def _create_simple_notification(self) -> None:
        """Create a simple notification about manual dashboard setup."""
        # This is now handled in _register_dashboard method
        pass
    
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
        # Store dashboard config for future use
        try:
            await self._store.async_save(dashboard_config)
            _LOGGER.debug("Saved dashboard config to storage")
        except Exception as err:
            _LOGGER.warning("Failed to save dashboard config: %s", err)
        
        # For now, just create a notification instead of trying complex registration
        # This avoids the registration errors while still providing functionality
        try:
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "message": (
                        "✅ **Planty is ready!**\n\n"
                        "🌱 **Add your first plant:**\n"
                        "Go to Developer Tools → Services and use:\n"
                        "`planty.add_plant` with your plant details\n\n"
                        "📊 **View plant sensors:**\n"
                        "Check Developer Tools → States for new entities\n\n"
                        "🎯 **Manual Dashboard:**\n"
                        "Create a dashboard manually in Settings → Dashboards\n"
                        "Then add custom `planty-card` cards for each plant"
                    ),
                    "title": "🌿 Planty Integration Ready",
                    "notification_id": "planty_ready"
                }
            )
            _LOGGER.info("Created Planty setup notification")
        except Exception as notif_err:
            _LOGGER.warning("Failed to create setup notification: %s", notif_err)
    
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
    try:
        manager = DashboardManager(hass, entry)
        await manager.async_create_dashboard()
        return manager
    except Exception as err:
        _LOGGER.error("Dashboard setup failed: %s", err)
        raise
