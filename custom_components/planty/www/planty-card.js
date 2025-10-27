class PlantyCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('You need to define an entity');
    }
    this.config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    if (this.config) {
      this.updateCard();
    }
  }

  render() {
    const style = `
      <style>
        .plant-card {
          background: var(--card-background-color);
          border-radius: 12px;
          padding: 16px;
          box-shadow: var(--shadow-elevation-2dp);
          cursor: pointer;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }
        
        .plant-card:hover {
          box-shadow: var(--shadow-elevation-4dp);
          transform: translateY(-2px);
        }
        
        .plant-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;
        }
        
        .plant-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .plant-icon {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: linear-gradient(135deg, #81C784, #4CAF50);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 20px;
        }
        
        .plant-details h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        
        .plant-type {
          font-size: 12px;
          color: var(--secondary-text-color);
          margin: 2px 0 0 0;
        }
        
        .settings-button {
          background: none;
          border: none;
          cursor: pointer;
          padding: 4px;
          border-radius: 50%;
          color: var(--secondary-text-color);
          transition: background-color 0.2s;
        }
        
        .settings-button:hover {
          background-color: var(--divider-color);
        }
        
        .progress-container {
          margin: 16px 0;
        }
        
        .progress-bar {
          width: 100%;
          height: 8px;
          background-color: var(--divider-color);
          border-radius: 4px;
          overflow: hidden;
          position: relative;
        }
        
        .progress-fill {
          height: 100%;
          transition: width 0.3s ease, background-color 0.3s ease;
          border-radius: 4px;
        }
        
        .progress-fill.green {
          background: linear-gradient(90deg, #4CAF50, #81C784);
        }
        
        .progress-fill.orange {
          background: linear-gradient(90deg, #FF9800, #FFB74D);
        }
        
        .progress-fill.red {
          background: linear-gradient(90deg, #F44336, #EF5350);
        }
        
        .card-bottom {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        
        .status-info {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        
        .status-text {
          font-size: 14px;
          font-weight: 500;
        }
        
        .status-text.green {
          color: #4CAF50;
        }
        
        .status-text.orange {
          color: #FF9800;
        }
        
        .status-text.red {
          color: #F44336;
        }
        
        .status-detail {
          font-size: 12px;
          color: var(--secondary-text-color);
        }
        
        .water-button {
          background: #2196F3;
          color: white;
          border: none;
          border-radius: 20px;
          padding: 8px 16px;
          cursor: pointer;
          font-size: 12px;
          font-weight: 500;
          transition: background-color 0.2s;
          display: flex;
          align-items: center;
          gap: 4px;
        }
        
        .water-button:hover {
          background: #1976D2;
        }
        
        .water-button:disabled {
          background: var(--disabled-color);
          cursor: not-allowed;
        }
        
        .modal {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          display: none;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }
        
        .modal-content {
          background: var(--card-background-color);
          border-radius: 8px;
          padding: 24px;
          max-width: 400px;
          width: 90%;
          max-height: 80vh;
          overflow-y: auto;
        }
        
        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }
        
        .modal-title {
          font-size: 18px;
          font-weight: 500;
          margin: 0;
        }
        
        .close-button {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          color: var(--secondary-text-color);
        }
        
        .form-group {
          margin-bottom: 16px;
        }
        
        .form-label {
          display: block;
          margin-bottom: 4px;
          font-size: 14px;
          font-weight: 500;
        }
        
        .form-input, .form-select {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          background: var(--card-background-color);
          color: var(--primary-text-color);
          box-sizing: border-box;
        }
        
        .button-group {
          display: flex;
          gap: 8px;
          justify-content: flex-end;
        }
        
        .btn {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
        }
        
        .btn-primary {
          background: #2196F3;
          color: white;
        }
        
        .btn-secondary {
          background: var(--divider-color);
          color: var(--primary-text-color);
        }
      </style>
    `;

    this.shadowRoot.innerHTML = style + `
      <div class="plant-card" onclick="this.openSettings()">
        <div class="plant-header">
          <div class="plant-info">
            <div class="plant-icon">
              <ha-icon icon="mdi:leaf"></ha-icon>
            </div>
            <div class="plant-details">
              <h3 class="plant-name">${this.config.name || 'Unknown Plant'}</h3>
              <div class="plant-type">${this.getPlantTypeName()}</div>
            </div>
          </div>
          <button class="settings-button" onclick="event.stopPropagation(); this.openSettings()">
            <ha-icon icon="mdi:cog"></ha-icon>
          </button>
        </div>
        
        <div class="progress-container">
          <div class="progress-bar">
            <div class="progress-fill" id="progress-fill"></div>
          </div>
        </div>
        
        <div class="card-bottom">
          <div class="status-info">
            <div class="status-text" id="status-text">Optimal</div>
            <div class="status-detail" id="status-detail">58.0%</div>
          </div>
          <button class="water-button" onclick="event.stopPropagation(); this.handleWaterClick()" id="water-button">
            <ha-icon icon="mdi:water"></ha-icon>
            Water
          </button>
        </div>
      </div>
      
      <!-- Settings Modal -->
      <div class="modal" id="settings-modal">
        <div class="modal-content">
          <div class="modal-header">
            <h3 class="modal-title">Plant Settings</h3>
            <button class="close-button" onclick="this.closeSettings()">&times;</button>
          </div>
          
          <div class="form-group">
            <label class="form-label">Plant Name</label>
            <input type="text" class="form-input" id="plant-name-input" />
          </div>
          
          <div class="form-group">
            <label class="form-label">Plant Type</label>
            <select class="form-select" id="plant-type-select">
              <option value="">Select plant type...</option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">Watering Mode</label>
            <select class="form-select" id="watering-mode-select">
              <option value="manual">Manual (Timer-based)</option>
              <option value="sensor">Sensor (Humidity-based)</option>
            </select>
          </div>
          
          <div class="form-group" id="sensor-group" style="display: none;">
            <label class="form-label">Humidity Sensor</label>
            <select class="form-select" id="humidity-sensor-select">
              <option value="">Select humidity sensor...</option>
            </select>
          </div>
          
          <div class="form-group" id="interval-group">
            <label class="form-label">Watering Interval (days)</label>
            <input type="number" class="form-input" id="watering-interval-input" min="1" max="30" />
          </div>
          
          <div class="button-group">
            <button class="btn btn-secondary" onclick="this.closeSettings()">Cancel</button>
            <button class="btn btn-primary" onclick="this.saveSettings()">Save</button>
          </div>
        </div>
      </div>
      
      <!-- Water Date Modal -->
      <div class="modal" id="water-modal">
        <div class="modal-content">
          <div class="modal-header">
            <h3 class="modal-title">Water Plant</h3>
            <button class="close-button" onclick="this.closeWaterModal()">&times;</button>
          </div>
          
          <div class="form-group">
            <label class="form-label">Watering Date</label>
            <input type="date" class="form-input" id="water-date-input" />
          </div>
          
          <div class="button-group">
            <button class="btn btn-secondary" onclick="this.closeWaterModal()">Cancel</button>
            <button class="btn btn-primary" onclick="this.waterPlant()">Water Plant</button>
          </div>
        </div>
      </div>
    `;

    // Bind methods to this context
    this.openSettings = this.openSettings.bind(this);
    this.closeSettings = this.closeSettings.bind(this);
    this.saveSettings = this.saveSettings.bind(this);
    this.handleWaterClick = this.handleWaterClick.bind(this);
    this.closeWaterModal = this.closeWaterModal.bind(this);
    this.waterPlant = this.waterPlant.bind(this);
  }

  updateCard() {
    if (!this._hass || !this.config.entity) return;

    const entity = this._hass.states[this.config.entity];
    if (!entity) return;

    const attributes = entity.attributes || {};
    const progressPercentage = attributes.progress_percentage || 0;
    const colorState = attributes.color_state || 'green';
    const wateringMode = attributes.watering_mode || 'manual';

    // Update progress bar
    const progressFill = this.shadowRoot.getElementById('progress-fill');
    if (progressFill) {
      progressFill.style.width = `${progressPercentage}%`;
      progressFill.className = `progress-fill ${colorState}`;
    }

    // Update status text and detail
    const statusText = this.shadowRoot.getElementById('status-text');
    const statusDetail = this.shadowRoot.getElementById('status-detail');
    
    if (statusText && statusDetail) {
      const { text, detail } = this.getStatusInfo(entity, attributes, wateringMode);
      statusText.textContent = text;
      statusText.className = `status-text ${colorState}`;
      statusDetail.textContent = detail;
    }

    // Update water button for manual mode
    const waterButton = this.shadowRoot.getElementById('water-button');
    if (waterButton && wateringMode === 'manual') {
      waterButton.style.display = 'flex';
    } else if (waterButton) {
      waterButton.style.display = 'none';
    }
  }

  getStatusInfo(entity, attributes, wateringMode) {
    if (wateringMode === 'sensor') {
      const humidity = attributes.current_humidity;
      if (humidity !== undefined) {
        return {
          text: this.getStatusText(attributes.color_state),
          detail: `${humidity.toFixed(1)}%`
        };
      }
      return { text: 'Unknown', detail: 'No sensor data' };
    } else {
      const daysSince = attributes.days_since_watered || 0;
      const interval = attributes.watering_interval || 7;
      const daysUntil = Math.max(0, interval - daysSince);
      
      return {
        text: this.getStatusText(attributes.color_state),
        detail: daysUntil > 0 ? `${daysUntil} days left` : 'Water now'
      };
    }
  }

  getStatusText(colorState) {
    switch (colorState) {
      case 'red': return 'Needs Water';
      case 'orange': return 'Watering Soon';
      case 'green': return 'Optimal';
      default: return 'Unknown';
    }
  }

  getPlantTypeName() {
    const plantType = this.config.plant_type;
    if (!plantType || !this._hass) return 'Custom Plant';
    
    // This would ideally fetch from the plant database
    // For now, just format the plant type nicely
    return plantType.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  }

  openSettings() {
    const modal = this.shadowRoot.getElementById('settings-modal');
    if (modal) {
      // Populate current values
      const nameInput = this.shadowRoot.getElementById('plant-name-input');
      const typeSelect = this.shadowRoot.getElementById('plant-type-select');
      const modeSelect = this.shadowRoot.getElementById('watering-mode-select');
      const intervalInput = this.shadowRoot.getElementById('watering-interval-input');

      if (nameInput) nameInput.value = this.config.name || '';
      if (typeSelect) typeSelect.value = this.config.plant_type || '';
      if (modeSelect) {
        modeSelect.value = this.config.watering_mode || 'manual';
        this.toggleWateringMode(modeSelect.value);
      }
      if (intervalInput) intervalInput.value = this.config.watering_interval || 7;

      // Populate plant types and sensors (would need integration with HA)
      this.populateDropdowns();

      modal.style.display = 'flex';
    }
  }

  closeSettings() {
    const modal = this.shadowRoot.getElementById('settings-modal');
    if (modal) {
      modal.style.display = 'none';
    }
  }

  saveSettings() {
    const nameInput = this.shadowRoot.getElementById('plant-name-input');
    const typeSelect = this.shadowRoot.getElementById('plant-type-select');
    const modeSelect = this.shadowRoot.getElementById('watering-mode-select');
    const sensorSelect = this.shadowRoot.getElementById('humidity-sensor-select');
    const intervalInput = this.shadowRoot.getElementById('watering-interval-input');

    if (!this._hass) return;

    const data = {
      plant_id: this.config.plant_id,
      name: nameInput?.value,
      plant_type: typeSelect?.value,
      watering_mode: modeSelect?.value,
      humidity_sensor: sensorSelect?.value,
      watering_interval: parseInt(intervalInput?.value) || 7
    };

    this._hass.callService('planty', 'update_plant_settings', data);
    this.closeSettings();
  }

  handleWaterClick() {
    const modal = this.shadowRoot.getElementById('water-modal');
    if (modal) {
      // Set today as default date
      const dateInput = this.shadowRoot.getElementById('water-date-input');
      if (dateInput) {
        dateInput.value = new Date().toISOString().split('T')[0];
      }
      modal.style.display = 'flex';
    }
  }

  closeWaterModal() {
    const modal = this.shadowRoot.getElementById('water-modal');
    if (modal) {
      modal.style.display = 'none';
    }
  }

  waterPlant() {
    const dateInput = this.shadowRoot.getElementById('water-date-input');
    if (!this._hass || !dateInput) return;

    const wateredDate = new Date(dateInput.value).toISOString();
    
    this._hass.callService('planty', 'water_plant_custom_date', {
      plant_id: this.config.plant_id,
      watered_date: wateredDate
    });

    this.closeWaterModal();
  }

  toggleWateringMode(mode) {
    const sensorGroup = this.shadowRoot.getElementById('sensor-group');
    const intervalGroup = this.shadowRoot.getElementById('interval-group');

    if (sensorGroup && intervalGroup) {
      if (mode === 'sensor') {
        sensorGroup.style.display = 'block';
        intervalGroup.style.display = 'none';
      } else {
        sensorGroup.style.display = 'none';
        intervalGroup.style.display = 'block';
      }
    }
  }

  populateDropdowns() {
    // This would populate with actual data from Home Assistant
    // For now, using placeholder implementation
  }

  getCardSize() {
    return 2;
  }

  static getConfigElement() {
    return document.createElement('planty-card-editor');
  }

  static getStubConfig() {
    return {
      entity: '',
      name: 'My Plant',
      plant_type: 'pothos',
      watering_mode: 'manual'
    };
  }
}

customElements.define('planty-card', PlantyCard);

// Register the card with HACS
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'planty-card',
  name: 'Planty Card',
  description: 'A custom card for displaying plant watering status'
});

console.info('Planty Card loaded');
