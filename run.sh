#!/usr/bin/with-contenv bashio

# ==============================================================================
# Planty Add-on startup script
# ==============================================================================

bashio::log.info "Starting Planty Plant Watering Manager..."

# Parse configuration
export LOG_LEVEL=$(bashio::config 'log_level')
export AUTO_CREATE_DASHBOARD=$(bashio::config 'auto_create_dashboard')
export IMAGE_STORAGE_PATH=$(bashio::config 'image_storage_path')
export BACKUP_ENABLED=$(bashio::config 'backup_enabled')
export BACKUP_INTERVAL=$(bashio::config 'backup_interval')

# Get Home Assistant details
export SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN}"
export HOMEASSISTANT_URL="http://supervisor/core"

bashio::log.info "Configuration loaded:"
bashio::log.info "  Log Level: ${LOG_LEVEL}"
bashio::log.info "  Auto Create Dashboard: ${AUTO_CREATE_DASHBOARD}"
bashio::log.info "  Image Storage Path: ${IMAGE_STORAGE_PATH}"
bashio::log.info "  Backup Enabled: ${BACKUP_ENABLED}"

# Create necessary directories
mkdir -p /data/planty
mkdir -p "${IMAGE_STORAGE_PATH}"
mkdir -p /var/log/nginx

# Set permissions
chown -R nginx:nginx /var/log/nginx
chmod -R 755 "${IMAGE_STORAGE_PATH}"

# Start nginx
bashio::log.info "Starting nginx..."
nginx -g "daemon on;"

# Start Planty service
bashio::log.info "Starting Planty service..."
cd /app
exec python3 -m planty.main
