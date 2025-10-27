"""Constants for the Planty integration."""
from __future__ import annotations

DOMAIN = "planty"
DEFAULT_NAME = "Planty"

# Configuration keys
CONF_PLANTS = "plants"
CONF_PLANT_NAME = "plant_name"
CONF_PLANT_TYPE = "plant_type"
CONF_CUSTOM_NAME = "custom_name"
CONF_WATERING_MODE = "watering_mode"
CONF_HUMIDITY_SENSOR = "humidity_sensor"
CONF_WATERING_INTERVAL = "watering_interval"
CONF_PLANT_IMAGE = "plant_image"

# Watering modes
WATERING_MODE_SENSOR = "sensor"
WATERING_MODE_MANUAL = "manual"

# Default values
DEFAULT_WATERING_INTERVAL = 7  # days
DEFAULT_HUMIDITY_MIN = 30
DEFAULT_HUMIDITY_MAX = 70

# Services
SERVICE_WATER_PLANT = "water_plant"
SERVICE_ADD_PLANT = "add_plant"
SERVICE_REMOVE_PLANT = "remove_plant"
SERVICE_UPDATE_IMAGE = "update_plant_image"
SERVICE_ADD_PLANT_TO_DASHBOARD = "add_plant_to_dashboard"
SERVICE_REMOVE_PLANT_FROM_DASHBOARD = "remove_plant_from_dashboard"
SERVICE_WATER_PLANT_CUSTOM_DATE = "water_plant_custom_date"
SERVICE_UPDATE_PLANT_SETTINGS = "update_plant_settings"

# Entity types
SENSOR_TYPES = {
    "humidity": {
        "name": "Soil Humidity",
        "icon": "mdi:water-percent",
        "unit": "%",
        "device_class": "humidity",
    },
    "days_until_water": {
        "name": "Days Until Watering",
        "icon": "mdi:calendar-clock",
        "unit": "days",
        "device_class": None,
    },
    "last_watered": {
        "name": "Last Watered",
        "icon": "mdi:calendar-check",
        "unit": None,
        "device_class": "timestamp",
    },
    "water_status": {
        "name": "Water Status",
        "icon": "mdi:water-alert",
        "unit": None,
        "device_class": None,
    },
}

# Plant status values
PLANT_STATUS_HEALTHY = "healthy"
PLANT_STATUS_NEEDS_WATER = "needs_water"
PLANT_STATUS_OVERDUE = "overdue"
PLANT_STATUS_UNKNOWN = "unknown"
