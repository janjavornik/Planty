"""Config flow for Planty integration."""
from __future__ import annotations

import json
import logging
import os
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_PLANT_NAME,
    CONF_PLANT_TYPE,
    CONF_CUSTOM_NAME,
    CONF_WATERING_MODE,
    CONF_HUMIDITY_SENSOR,
    CONF_WATERING_INTERVAL,
    WATERING_MODE_SENSOR,
    WATERING_MODE_MANUAL,
    DEFAULT_WATERING_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class PlantyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Planty."""

    VERSION = 1
    
    def __init__(self) -> None:
        """Initialize the config flow."""
        self._plants_db: dict[str, Any] = {}
        self._plants: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # Load plants database
        await self._load_plants_database()
        
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({}),
                description_placeholders={
                    "plant_count": str(len(self._plants_db.get("plants", {}))),
                }
            )

        return self.async_create_entry(
            title="Planty Plant Manager", 
            data={"plants": self._plants}
        )

    async def async_step_add_plant(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle adding a plant."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Validate the plant configuration
            plant_name = user_input.get(CONF_PLANT_NAME)
            plant_type = user_input.get(CONF_PLANT_TYPE, "custom")
            custom_name = user_input.get(CONF_CUSTOM_NAME, "")
            watering_mode = user_input.get(CONF_WATERING_MODE, WATERING_MODE_MANUAL)
            humidity_sensor = user_input.get(CONF_HUMIDITY_SENSOR)
            watering_interval = user_input.get(CONF_WATERING_INTERVAL, DEFAULT_WATERING_INTERVAL)

            # Use custom name if plant type is custom
            if plant_type == "custom":
                if not custom_name:
                    errors[CONF_CUSTOM_NAME] = "custom_name_required"
                else:
                    plant_name = custom_name

            # Validate sensor mode requirements
            if watering_mode == WATERING_MODE_SENSOR and not humidity_sensor:
                errors[CONF_HUMIDITY_SENSOR] = "sensor_required"

            if not errors:
                # Get plant data from database if not custom
                plant_data = {}
                if plant_type != "custom" and plant_type in self._plants_db.get("plants", {}):
                    plant_data = self._plants_db["plants"][plant_type].copy()

                # Create plant configuration
                plant_config = {
                    "name": plant_name,
                    "type": plant_type,
                    "watering_mode": watering_mode,
                    "humidity_sensor": humidity_sensor,
                    "watering_interval": watering_interval,
                    "plant_data": plant_data,
                }
                
                self._plants.append(plant_config)
                
                return self.async_show_form(
                    step_id="add_plant_success",
                    description_placeholders={"plant_name": plant_name}
                )

        # Build plant options for dropdown
        plant_options = [{"value": "custom", "label": "Custom Plant"}]
        for plant_id, plant_info in self._plants_db.get("plants", {}).items():
            plant_options.append({
                "value": plant_id,
                "label": f"{plant_info['common_name']} ({plant_info['difficulty']})"
            })

        # Get available humidity sensors
        humidity_sensors = await self._get_humidity_sensors()

        data_schema = vol.Schema({
            vol.Required(CONF_PLANT_TYPE, default="custom"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=plant_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(CONF_CUSTOM_NAME): cv.string,
            vol.Required(CONF_WATERING_MODE, default=WATERING_MODE_MANUAL): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": WATERING_MODE_MANUAL, "label": "Manual Countdown"},
                        {"value": WATERING_MODE_SENSOR, "label": "Soil Humidity Sensor"},
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(CONF_HUMIDITY_SENSOR): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["sensor"],
                    device_class=["humidity"],
                )
            ),
            vol.Required(CONF_WATERING_INTERVAL, default=DEFAULT_WATERING_INTERVAL): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=30,
                    step=1,
                    unit_of_measurement="days",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
        })

        return self.async_show_form(
            step_id="add_plant",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "available_sensors": str(len(humidity_sensors)),
            }
        )

    async def async_step_add_plant_success(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle successful plant addition."""
        if user_input is not None:
            # User wants to add another plant
            if user_input.get("add_another"):
                return await self.async_step_add_plant()
            else:
                # Finish configuration
                return self.async_create_entry(
                    title="Planty Plant Manager",
                    data={"plants": self._plants}
                )

        return self.async_show_form(
            step_id="add_plant_success",
            data_schema=vol.Schema({
                vol.Optional("add_another", default=False): cv.boolean,
            }),
        )

    async def _load_plants_database(self) -> None:
        """Load the plants database."""
        try:
            integration_path = os.path.dirname(__file__)
            plants_file = os.path.join(integration_path, "plants_data.json")
            
            def load_plants():
                with open(plants_file, encoding="utf-8") as f:
                    return json.load(f)
            
            self._plants_db = await self.hass.async_add_executor_job(load_plants)
        except (FileNotFoundError, json.JSONDecodeError) as err:
            _LOGGER.error("Failed to load plants database: %s", err)
            self._plants_db = {"plants": {}}

    async def _get_humidity_sensors(self) -> list[str]:
        """Get available humidity sensors."""
        sensors = []
        for entity_id, entity in self.hass.states.async_all().items():
            if (
                entity_id.startswith("sensor.")
                and entity.attributes.get("device_class") == "humidity"
            ):
                sensors.append(entity_id)
        return sensors

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlowHandler:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Planty."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("auto_dashboard", default=True): cv.boolean,
                vol.Optional("default_image_crop", default=True): cv.boolean,
            }),
        )
