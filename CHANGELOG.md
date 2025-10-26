# Changelog

All notable changes to Planty will be documented in this file.

## [1.0.0] - 2024-01-01

### Added
- Complete transformation from Home Assistant custom integration to add-on
- Modern web interface with responsive design
- Real-time WebSocket communication for live updates
- Plant image upload and management
- Home Assistant sensor integration
- Material Design UI with beautiful plant cards
- Status dashboard with plant health overview
- Support for 15+ common houseplants with pre-configured settings
- Dual watering modes: manual timers and humidity sensors
- Automated backup system
- Docker containerization for easy deployment

### Changed
- Architecture completely redesigned as a Home Assistant Add-on
- Installation method changed to add-on store
- Web-based configuration instead of YAML
- Enhanced plant management with full CRUD operations
- Improved plant status tracking and visualization

### Technical Changes
- Python backend with aiohttp web server
- nginx reverse proxy for static files and API routing
- WebSocket support for real-time updates
- JSON-based storage system
- REST API for plant management
- Container-based deployment with proper health checks

### Migration Notes
- This version is not compatible with the previous custom integration
- Users need to uninstall the old integration and install the new add-on
- Plant data will need to be re-entered through the new web interface
- Home Assistant sensors will be recreated with new entity names
