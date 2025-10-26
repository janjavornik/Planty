# Planty - Plant Watering Manager Add-on

[![GitHub release](https://img.shields.io/github/release/planty/planty.svg)](https://github.com/planty/planty/releases/)
[![License](https://img.shields.io/github/license/planty/planty.svg)](LICENSE)
[![Docker Image](https://img.shields.io/docker/image-size/planty/planty-addon)](https://hub.docker.com/r/planty/planty-addon)

A comprehensive Home Assistant Add-on for managing houseplant watering schedules with a beautiful web interface and Home Assistant integration.

## Features

🌱 **Plant Database**: Pre-loaded with 15+ common houseplants and their optimal watering schedules  
📊 **Dual Tracking Modes**: Manual countdown timers or soil humidity sensor monitoring  
🎨 **Beautiful Web Interface**: Modern, responsive web UI for plant management  
📸 **Custom Images**: Upload plant photos for personalized plant cards  
🔔 **Smart Status**: Visual indicators for healthy, needs water, and overdue plants  
⚡ **Easy Setup**: Add-on installation with web-based configuration  
🏠 **Home Assistant Integration**: Creates sensors and entities in Home Assistant  
🔄 **Real-time Updates**: WebSocket connection for live plant status updates

## Installation

### Via Home Assistant Add-on Store (Recommended)

1. Navigate to **Supervisor** → **Add-on Store** in Home Assistant
2. Click the three dots menu → **Repositories**
3. Add `https://github.com/planty/planty` as a repository
4. Find "Planty - Plant Watering Manager" in the add-on store
5. Click **Install**
6. Configure the add-on options (see Configuration section)
7. Start the add-on
8. Access the web interface via the **Web UI** button or `http://homeassistant.local:8099`

### Manual Installation

1. Clone this repository to your Home Assistant add-ons directory:
   ```bash
   cd /addons
   git clone https://github.com/planty/planty.git
   ```
2. Navigate to **Supervisor** → **Add-on Store** → **Local Add-ons**
3. Find "Planty" and click **Install**
4. Configure and start the add-on

## Quick Start

1. **Install Add-on**: Follow the installation steps above
2. **Start Add-on**: Configure options and start the Planty add-on
3. **Access Web UI**: Open the web interface from the add-on page
4. **Add Plants**: Use the web interface to add your first plants
5. **Choose Mode**: Select manual countdown or humidity sensor tracking
6. **Monitor Plants**: View plant status in both the web UI and Home Assistant
7. **Water Plants**: Use the web interface or Home Assistant automations

## Plant Database

Planty includes optimal watering data for popular houseplants:

- **Snake Plant**: 14 days, 20-40% humidity
- **Pothos**: 7 days, 40-60% humidity  
- **Peace Lily**: 5 days, 50-70% humidity
- **Monstera**: 7 days, 50-70% humidity
- **ZZ Plant**: 14 days, 20-40% humidity
- And 15+ more...

## Configuration Options

### Watering Modes

**Manual Mode**: Set watering intervals and use countdown timers
- Perfect for beginners
- No additional hardware required
- Simple tap-to-water interface

**Sensor Mode**: Connect soil humidity sensors for automatic monitoring
- Works with ESPHome, Zigbee, and other HA-compatible sensors
- Real-time soil moisture tracking
- Smart watering recommendations

## Configuration

The add-on can be configured with the following options:

### Add-on Options

- **log_level**: Set logging level (trace, debug, info, notice, warning, error, fatal)
- **auto_create_dashboard**: Automatically create Home Assistant dashboard (default: true)
- **image_storage_path**: Path to store plant images (default: /share/planty/images)
- **backup_enabled**: Enable automatic backups (default: true)
- **backup_interval**: Backup interval in hours (default: 24)

### Plant Cards

Each plant gets its own card in the web interface showing:
- Plant name and type
- Current water status (healthy/needs water/overdue)
- Days until next watering or current humidity level
- Custom plant image
- One-tap watering button
- Edit and delete options

## Home Assistant Integration

Planty automatically creates sensors in Home Assistant for each plant:

### Sensors Created
- `sensor.planty_{plant_id}_water_status` - Current water status (healthy/needs_water/overdue)
- `sensor.planty_{plant_id}_days_until_water` - Days until next watering
- `sensor.planty_{plant_id}_last_watered` - Timestamp of last watering
- `sensor.planty_{plant_id}_humidity` - Current soil humidity (sensor mode only)

### Events
- `planty_plant_watered` - Fired when a plant is watered
- `planty_plant_added` - Fired when a new plant is added
- `planty_plant_updated` - Fired when plant data is updated

## Web Interface Features

### Modern Design
- Responsive layout that works on desktop and mobile
- Material Design icons and styling
- Real-time updates via WebSocket connection
- Dark/light theme support (automatic)

### Plant Management
- Add/edit/delete plants through the web UI
- Upload custom plant images
- Bulk operations for multiple plants
- Search and filter functionality

### Image Management
- Upload custom plant photos through the web interface
- Images are automatically processed and stored
- Accessible via Home Assistant's www directory
- Support for common image formats (JPG, PNG, GIF, WebP)

## Automations

Create powerful plant care automations:

```yaml
# Remind when plants need water
automation:
  - alias: "Plant Watering Reminder"
    trigger:
      - platform: state
        entity_id: sensor.planty_pothos_water_status
        to: "needs_water"
    action:
      - service: notify.mobile_app
        data:
          message: "🌱 Your Pothos needs watering!"

# Auto-water plants based on humidity sensor
automation:
  - alias: "Auto-water based on humidity"
    trigger:
      - platform: numeric_state
        entity_id: sensor.planty_monstera_humidity
        below: 30
    action:
      - service: switch.turn_on
        entity_id: switch.plant_watering_pump
      - delay: '00:00:30'
      - service: switch.turn_off
        entity_id: switch.plant_watering_pump
```

## Troubleshooting

### Add-on Issues
**Add-on won't start**: Check the add-on logs for error messages and ensure all required options are configured

**Web UI not accessible**: Verify the add-on is running and check port 8099 is not blocked by firewall

**Plants not syncing to Home Assistant**: Check the Home Assistant API token and ensure the add-on has proper permissions

### Plant Issues
**Humidity sensor not working**: Verify the sensor entity exists in Home Assistant and has device_class: humidity

**Images not displaying**: Check that the image storage path is writable and accessible

**Plant status incorrect**: Verify watering intervals and last watered dates are correct

### Network Issues
**WebSocket connection fails**: Check network connectivity and firewall settings

**API requests failing**: Verify Home Assistant is accessible and API tokens are valid

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Add plants to the database via pull request
4. Submit bug reports and feature requests

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/planty/planty/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/planty/planty/discussions)
- 💬 **Community**: [Home Assistant Forum](https://community.home-assistant.io/)

## License

MIT License - see [LICENSE](LICENSE) for details.

---

Made with 🌱 for the Home Assistant community
