class PlantySettingsCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    this.config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
  }

  render() {
    const style = `
      <style>
        .settings-card {
          background: var(--card-background-color);
          border-radius: 12px;
          padding: 20px;
          margin-bottom: 16px;
          box-shadow: var(--shadow-elevation-2dp);
        }
        
        .settings-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 16px;
        }
        
        .settings-title {
          font-size: 18px;
          font-weight: 500;
          margin: 0;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .action-buttons {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }
        
        .action-button {
          background: var(--primary-color);
          color: white;
          border: none;
          border-radius: 8px;
          padding: 8px 16px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 6px;
          transition: background-color 0.2s;
        }
        
        .action-button:hover {
          background: var(--dark-primary-color);
        }
        
        .action-button.secondary {
          background: var(--divider-color);
          color: var(--primary-text-color);
        }
        
        .action-button.secondary:hover {
          background: var(--disabled-color);
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
          max-width: 500px;
          width: 90%;
          max-height: 80vh;
          overflow-y: auto;
        }
        
        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }
        
        .modal-title {
          font-size: 20px;
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
          margin-bottom: 6px;
          font-size: 14px;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        
        .form-input, .form-select {
          width: 100%;
          padding: 10px 12px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          background: var(--card-background-color);
          color: var(--primary-text-color);
          box-sizing: border-box;
          font-size: 14px;
        }
        
        .form-input:focus, .form-select:focus {
          outline: none;
          border-color: var(--primary-color);
        }
        
        .button-group {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
          margin-top: 24px;
        }
        
        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background-color 0.2s;
        }
        
        .btn-primary {
          background: var(--primary-color);
          color: white;
        }
        
        .btn-primary:hover {
          background: var(--dark-primary-color);
        }
        
        .btn-secondary {
          background: var(--divider-color);
          color: var(--primary-text-color);
        }
        
        .btn-secondary:hover {
          background: var(--disabled-color);
        }
        
        .plant-type-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 12px;
          margin-top: 12px;
        }
        
        .plant-type-option {
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          padding: 12px;
          cursor: pointer;
          transition: all 0.2s;
          background: var(--card-background-color);
        }
        
        .plant-type-option:hover {
          border-color: var(--primary-color);
          background: var(--primary-color);
          color: white;
        }
        
        .plant-type-option.selected {
          border-color: var(--primary-color);
          background: var(--primary-color);
          color: white;
        }
        
        .plant-type-name {
          font-weight: 500;
          margin-bottom: 4px;
        }
        
        .plant-type-details {
          font-size: 12px;
          opacity: 0.8;
        }
        
        @media (max-width: 600px) {
          .action-buttons {
            flex-direction: column;
          }
          
          .action-button {
            justify-content: center;
          }
          
          .plant-type-grid {
            grid-template-columns: 1fr;
          }
        }
      </style>
    `;

    this.shadowRoot.innerHTML = style + `
      <div class="settings-card">
        <div class="settings-header">
          <h2 class="settings-title">
            <ha-icon icon="mdi:cog"></ha-icon>
            Plant Management
          </h2>
        </div>
        
        <div class="action-buttons">
          <button class="action-button" onclick="this.openAddPlantModal()">
            <ha-icon icon="mdi:plus"></ha-icon>
            Add Plant
          </button>
          <button class="action-button secondary" onclick="this.exportSettings()">
            <ha-icon icon="mdi:download"></ha-icon>
            Export
          </button>
          <button class="action-button secondary" onclick="this.importSettings()">
            <ha-icon icon="mdi:upload"></ha-icon>
            Import
          </button>
        </div>
      </div>
      
      <!-- Add Plant Modal -->
      <div class="modal" id="add-plant-modal">
        <div class="modal-content">
          <div class="modal-header">
            <h3 class="modal-title">Add New Plant</h3>
            <button class="close-button" onclick="this.closeAddPlantModal()">&times;</button>
          </div>
          
          <form id="add-plant-form">
            <div class="form-group">
              <label class="form-label">Plant Name *</label>
              <input type="text" class="form-input" id="new-plant-name" placeholder="Enter plant name" required />
            </div>
            
            <div class="form-group">
              <label class="form-label">Plant Type</label>
              <div class="plant-type-grid" id="plant-type-grid">
                <!-- Plant types will be populated here -->
              </div>
            </div>
            
            <div class="form-group">
              <label class="form-label">Watering Mode *</label>
              <select class="form-select" id="new-watering-mode" onchange="this.toggleWateringMode()">
                <option value="manual">Manual (Timer-based)</option>
                <option value="sensor">Sensor (Humidity-based)</option>
              </select>
            </div>
            
            <div class="form-group" id="new-sensor-group" style="display: none;">
              <label class="form-label">Humidity Sensor</label>
              <select class="form-select" id="new-humidity-sensor">
                <option value="">Select humidity sensor...</option>
              </select>
            </div>
            
            <div class="form-group" id="new-interval-group">
              <label class="form-label">Watering Interval (days)</label>
              <input type="number" class="form-input" id="new-watering-interval" min="1" max="30" value="7" />
            </div>
            
            <div class="button-group">
              <button type="button" class="btn btn-secondary" onclick="this.closeAddPlantModal()">Cancel</button>
              <button type="submit" class="btn btn-primary">Add Plant</button>
            </div>
          </form>
        </div>
      </div>
    `;

    // Bind methods to this context
    this.openAddPlantModal = this.openAddPlantModal.bind(this);
    this.closeAddPlantModal = this.closeAddPlantModal.bind(this);
    this.toggleWateringMode = this.toggleWateringMode.bind(this);
    this.exportSettings = this.exportSettings.bind(this);
    this.importSettings = this.importSettings.bind(this);

    // Set up form submission
    const form = this.shadowRoot.getElementById('add-plant-form');
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        this.addPlant();
      });
    }
  }

  openAddPlantModal() {
    const modal = this.shadowRoot.getElementById('add-plant-modal');
    if (modal) {
      this.populatePlantTypes();
      this.populateHumiditySensors();
      modal.style.display = 'flex';
    }
  }

  closeAddPlantModal() {
    const modal = this.shadowRoot.getElementById('add-plant-modal');
    if (modal) {
      modal.style.display = 'none';
      // Reset form
      const form = this.shadowRoot.getElementById('add-plant-form');
      if (form) form.reset();
      // Clear plant type selection
      const plantTypeGrid = this.shadowRoot.getElementById('plant-type-grid');
      if (plantTypeGrid) {
        plantTypeGrid.querySelectorAll('.plant-type-option').forEach(option => {
          option.classList.remove('selected');
        });
      }
    }
  }

  toggleWateringMode() {
    const modeSelect = this.shadowRoot.getElementById('new-watering-mode');
    const sensorGroup = this.shadowRoot.getElementById('new-sensor-group');
    const intervalGroup = this.shadowRoot.getElementById('new-interval-group');

    if (modeSelect && sensorGroup && intervalGroup) {
      if (modeSelect.value === 'sensor') {
        sensorGroup.style.display = 'block';
        intervalGroup.style.display = 'none';
      } else {
        sensorGroup.style.display = 'none';
        intervalGroup.style.display = 'block';
      }
    }
  }

  populatePlantTypes() {
    const grid = this.shadowRoot.getElementById('plant-type-grid');
    if (!grid) return;

    // Common plant types - in a real implementation this would come from the plant database
    const plantTypes = [
      { id: 'pothos', name: 'Pothos', interval: 7, description: 'Easy care vine' },
      { id: 'snake_plant', name: 'Snake Plant', interval: 14, description: 'Low maintenance' },
      { id: 'peace_lily', name: 'Peace Lily', interval: 5, description: 'Elegant flowers' },
      { id: 'monstera', name: 'Monstera', interval: 7, description: 'Split leaf beauty' },
      { id: 'zz_plant', name: 'ZZ Plant', interval: 14, description: 'Drought tolerant' },
      { id: 'rubber_tree', name: 'Rubber Tree', interval: 7, description: 'Glossy leaves' }
    ];

    let selectedType = null;

    grid.innerHTML = plantTypes.map(plant => `
      <div class="plant-type-option" data-plant-type="${plant.id}" onclick="this.selectPlantType('${plant.id}')">
        <div class="plant-type-name">${plant.name}</div>
        <div class="plant-type-details">Water every ${plant.interval} days • ${plant.description}</div>
      </div>
    `).join('');

    // Add click handlers
    grid.querySelectorAll('.plant-type-option').forEach(option => {
      option.addEventListener('click', () => {
        // Remove previous selection
        grid.querySelectorAll('.plant-type-option').forEach(opt => opt.classList.remove('selected'));
        // Select current
        option.classList.add('selected');
        selectedType = option.getAttribute('data-plant-type');
        
        // Update watering interval
        const intervalInput = this.shadowRoot.getElementById('new-watering-interval');
        const plant = plantTypes.find(p => p.id === selectedType);
        if (intervalInput && plant) {
          intervalInput.value = plant.interval;
        }
      });
    });
  }

  populateHumiditySensors() {
    const select = this.shadowRoot.getElementById('new-humidity-sensor');
    if (!select || !this._hass) return;

    // Find all humidity sensors
    const humiditySensors = Object.keys(this._hass.states)
      .filter(entityId => {
        const entity = this._hass.states[entityId];
        return entity.attributes?.device_class === 'humidity' && 
               entityId.startsWith('sensor.');
      })
      .map(entityId => ({
        id: entityId,
        name: this._hass.states[entityId].attributes?.friendly_name || entityId
      }));

    select.innerHTML = '<option value="">Select humidity sensor...</option>' +
      humiditySensors.map(sensor => 
        `<option value="${sensor.id}">${sensor.name}</option>`
      ).join('');
  }

  addPlant() {
    if (!this._hass) return;

    const nameInput = this.shadowRoot.getElementById('new-plant-name');
    const modeSelect = this.shadowRoot.getElementById('new-watering-mode');
    const sensorSelect = this.shadowRoot.getElementById('new-humidity-sensor');
    const intervalInput = this.shadowRoot.getElementById('new-watering-interval');

    // Get selected plant type
    const selectedTypeOption = this.shadowRoot.querySelector('.plant-type-option.selected');
    const plantType = selectedTypeOption ? selectedTypeOption.getAttribute('data-plant-type') : null;

    const data = {
      plant_name: nameInput?.value,
      plant_type: plantType,
      watering_mode: modeSelect?.value || 'manual',
      humidity_sensor: sensorSelect?.value,
      watering_interval: parseInt(intervalInput?.value) || 7
    };

    if (!data.plant_name) {
      alert('Please enter a plant name');
      return;
    }

    if (data.watering_mode === 'sensor' && !data.humidity_sensor) {
      alert('Please select a humidity sensor for sensor mode');
      return;
    }

    this._hass.callService('planty', 'add_plant', data);
    this.closeAddPlantModal();
  }

  exportSettings() {
    if (!this._hass) return;

    // Collect all planty plants data
    const plantyEntities = Object.keys(this._hass.states)
      .filter(entityId => entityId.startsWith('sensor.planty_') && entityId.endsWith('_water_status'))
      .map(entityId => ({
        entity_id: entityId,
        attributes: this._hass.states[entityId].attributes
      }));

    const exportData = {
      version: '1.0',
      exported_at: new Date().toISOString(),
      plants: plantyEntities
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'planty-settings.json';
    a.click();
    URL.revokeObjectURL(url);
  }

  importSettings() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const data = JSON.parse(e.target.result);
            // Process import data here
            alert('Settings imported successfully!');
          } catch (error) {
            alert('Invalid file format');
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  }

  getCardSize() {
    return 1;
  }

  static getStubConfig() {
    return {};
  }
}

customElements.define('planty-settings-card', PlantySettingsCard);

console.info('Planty Settings Card loaded');
