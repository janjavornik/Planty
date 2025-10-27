# Planty - Plant Watering Manager for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/planty/planty.svg)](https://github.com/planty/planty/releases/)
[![License](https://img.shields.io/github/license/planty/planty.svg)](LICENSE)

A comprehensive Home Assistant integration for managing houseplant watering schedules with beautiful Mushroom card dashboards.

## Features

🌱 **Plant Database**: Pre-loaded with 15+ common houseplants and their optimal watering schedules  
📊 **Dual Tracking Modes**: Manual countdown timers or soil humidity sensor monitoring  
🎨 **Beautiful Dashboards**: Auto-generated "My Plants" dashboard with Mushroom cards  
📸 **Custom Images**: Upload and crop plant photos for personalized cards  
🔔 **Smart Status**: Visual indicators for healthy, needs water, and overdue plants  
⚡ **Easy Setup**: Beginner-friendly configuration through Home Assistant UI

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu → "Custom repositories"
4. Add `https://github.com/planty/planty` as an Integration repository
5. Search for "Planty" and install
6. Restart Home Assistant
7. Go to Settings → Integrations → Add Integration → Search for "Planty"

### Manual Installation

1. Download the latest release from GitHub
2. Extract to `config/custom_components/planty/`
3. Restart Home Assistant
4. Add the integration via Settings → Integrations

## Quick Start

1. **Add Integration**: Go to Settings → Integrations → Add Integration → "Planty"
2. **Add Plants**: Use the setup wizard to add your first plants
3. **Choose Mode**: Select manual countdown or humidity sensor tracking
4. **View Dashboard**: Check the auto-created "My Plants" dashboard
5. **Water Plants**: Tap the water button or use voice commands

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

### Plant Cards

Each plant gets its own card showing:
- Plant name and type
- Current water status (healthy/needs water/overdue)
- Days until next watering or current humidity level
- Custom background image
- One-tap watering button

## Services

Planty provides several services for automation:

```yaml
# Water a plant
service: planty.water_plant
data:
  plant_id: "my_pothos"

# Add a new plant
service: planty.add_plant
data:
  plant_name: "Office Snake Plant"
  plant_type: "snake_plant"
  watering_mode: "manual"
  watering_interval: 14
```

## Image Management

Upload custom plant photos that are automatically:
- Cropped to square aspect ratio
- Resized to 300x300px for optimal card display
- Stored in `/config/www/planty/`
- Available as card backgrounds

## Dashboard Integration

Planty automatically creates a "My Plants" dashboard with:
- Responsive grid layout
- Mushroom card styling
- Plant status color coding
- Touch-friendly interface
- Mobile optimization

## Automations

Create powerful plant care automations:

```yaml
# Remind when plants need water
automation:
  - alias: "Plant Watering Reminder"
    trigger:
      - platform: state
        entity_id: sensor.pothos_water_status
        to: "needs_water"
    action:
      - service: notify.mobile_app
        data:
          message: "🌱 Your Pothos needs watering!"
```

## Troubleshooting

**Plant not showing up**: Check that the integration loaded successfully in Settings → Integrations

**Humidity sensor not working**: Verify the sensor entity is available and has device_class: humidity

**Images not displaying**: Check that files are in `/config/www/planty/` and accessible via `/local/planty/`

**Dashboard not created**: Enable "Auto-create dashboard" in integration options

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
