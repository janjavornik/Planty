class PlantyHeaderCard extends HTMLElement {
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
        .header-card {
          background: linear-gradient(135deg, #4CAF50, #81C784);
          color: white;
          border-radius: 12px;
          padding: 24px;
          margin-bottom: 16px;
          text-align: center;
          box-shadow: var(--shadow-elevation-2dp);
        }
        
        .header-icon {
          font-size: 48px;
          margin-bottom: 12px;
          display: block;
        }
        
        .header-title {
          font-size: 28px;
          font-weight: 600;
          margin: 0 0 8px 0;
          text-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        
        .header-subtitle {
          font-size: 16px;
          opacity: 0.9;
          margin: 0;
          font-weight: 400;
        }
        
        .stats-container {
          display: flex;
          justify-content: center;
          gap: 24px;
          margin-top: 16px;
        }
        
        .stat-item {
          text-align: center;
        }
        
        .stat-number {
          font-size: 24px;
          font-weight: 600;
          display: block;
        }
        
        .stat-label {
          font-size: 12px;
          opacity: 0.8;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        @media (max-width: 600px) {
          .header-card {
            padding: 20px;
          }
          
          .header-title {
            font-size: 24px;
          }
          
          .stats-container {
            gap: 16px;
          }
          
          .stat-number {
            font-size: 20px;
          }
        }
      </style>
    `;

    this.shadowRoot.innerHTML = style + `
      <div class="header-card">
        <ha-icon icon="mdi:leaf" class="header-icon"></ha-icon>
        <h1 class="header-title">${this.config.title || 'My Plants'}</h1>
        <p class="header-subtitle">${this.config.subtitle || 'Plant care made simple'}</p>
        <div class="stats-container" id="stats-container">
          <!-- Stats will be populated by updateStats() -->
        </div>
      </div>
    `;

    if (this._hass) {
      this.updateStats();
    }
  }

  updateStats() {
    if (!this._hass) return;

    // Count plant statuses
    let healthyCount = 0;
    let needsWaterCount = 0;
    let overdueCount = 0;

    // Find all planty water status sensors
    Object.keys(this._hass.states).forEach(entityId => {
      if (entityId.startsWith('sensor.planty_') && entityId.endsWith('_water_status')) {
        const entity = this._hass.states[entityId];
        const colorState = entity.attributes?.color_state;
        
        switch (colorState) {
          case 'green':
            healthyCount++;
            break;
          case 'orange':
            needsWaterCount++;
            break;
          case 'red':
            overdueCount++;
            break;
        }
      }
    });

    const statsContainer = this.shadowRoot.getElementById('stats-container');
    if (statsContainer) {
      statsContainer.innerHTML = `
        <div class="stat-item">
          <span class="stat-number">${healthyCount}</span>
          <span class="stat-label">Healthy</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">${needsWaterCount}</span>
          <span class="stat-label">Watering Soon</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">${overdueCount}</span>
          <span class="stat-label">Need Water</span>
        </div>
      `;
    }
  }

  getCardSize() {
    return 2;
  }

  static getStubConfig() {
    return {
      title: 'My Plants',
      subtitle: 'Plant care made simple'
    };
  }
}

customElements.define('planty-header-card', PlantyHeaderCard);

console.info('Planty Header Card loaded');
