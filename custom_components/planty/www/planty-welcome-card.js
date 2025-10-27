class PlantyWelcomeCard extends HTMLElement {
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
        .welcome-card {
          background: var(--card-background-color);
          border-radius: 12px;
          padding: 40px 24px;
          text-align: center;
          box-shadow: var(--shadow-elevation-2dp);
          border: 2px dashed var(--divider-color);
          margin: 20px 0;
        }
        
        .welcome-icon {
          font-size: 64px;
          color: var(--primary-color);
          margin-bottom: 20px;
          display: block;
          opacity: 0.7;
        }
        
        .welcome-title {
          font-size: 24px;
          font-weight: 600;
          margin: 0 0 12px 0;
          color: var(--primary-text-color);
        }
        
        .welcome-subtitle {
          font-size: 16px;
          color: var(--secondary-text-color);
          margin: 0 0 24px 0;
          line-height: 1.5;
        }
        
        .welcome-features {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          margin: 24px 0;
          text-align: left;
        }
        
        .feature-item {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 12px;
          background: var(--primary-color);
          color: white;
          border-radius: 8px;
          font-size: 14px;
        }
        
        .feature-icon {
          font-size: 20px;
          margin-top: 2px;
          flex-shrink: 0;
        }
        
        .feature-text {
          line-height: 1.4;
        }
        
        .get-started-button {
          background: var(--primary-color);
          color: white;
          border: none;
          border-radius: 8px;
          padding: 12px 24px;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          transition: all 0.2s;
          margin-top: 16px;
        }
        
        .get-started-button:hover {
          background: var(--dark-primary-color);
          transform: translateY(-2px);
          box-shadow: var(--shadow-elevation-4dp);
        }
        
        .tips-section {
          margin-top: 32px;
          padding-top: 24px;
          border-top: 1px solid var(--divider-color);
        }
        
        .tips-title {
          font-size: 18px;
          font-weight: 500;
          margin: 0 0 16px 0;
          color: var(--primary-text-color);
        }
        
        .tip-list {
          list-style: none;
          padding: 0;
          margin: 0;
          text-align: left;
        }
        
        .tip-item {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          padding: 8px 0;
          font-size: 14px;
          color: var(--secondary-text-color);
        }
        
        .tip-icon {
          color: var(--primary-color);
          font-size: 16px;
          margin-top: 2px;
        }
        
        @media (max-width: 600px) {
          .welcome-card {
            padding: 24px 16px;
          }
          
          .welcome-icon {
            font-size: 48px;
          }
          
          .welcome-title {
            font-size: 20px;
          }
          
          .welcome-features {
            grid-template-columns: 1fr;
          }
        }
      </style>
    `;

    this.shadowRoot.innerHTML = style + `
      <div class="welcome-card">
        <ha-icon icon="mdi:leaf-circle" class="welcome-icon"></ha-icon>
        
        <h2 class="welcome-title">Welcome to Planty!</h2>
        <p class="welcome-subtitle">
          Start tracking your houseplants and never forget to water them again.<br>
          Your green friends will thank you! 🌱
        </p>
        
        <div class="welcome-features">
          <div class="feature-item">
            <ha-icon icon="mdi:calendar-clock" class="feature-icon"></ha-icon>
            <div class="feature-text">
              <strong>Smart Reminders</strong><br>
              Get notified when your plants need water
            </div>
          </div>
          
          <div class="feature-item">
            <ha-icon icon="mdi:water-percent" class="feature-icon"></ha-icon>
            <div class="feature-text">
              <strong>Sensor Integration</strong><br>
              Connect humidity sensors for automatic monitoring
            </div>
          </div>
          
          <div class="feature-item">
            <ha-icon icon="mdi:database" class="feature-icon"></ha-icon>
            <div class="feature-text">
              <strong>Plant Database</strong><br>
              Pre-configured settings for 15+ common plants
            </div>
          </div>
          
          <div class="feature-item">
            <ha-icon icon="mdi:chart-line" class="feature-icon"></ha-icon>
            <div class="feature-text">
              <strong>Visual Progress</strong><br>
              See water levels with colorful progress bars
            </div>
          </div>
        </div>
        
        <button class="get-started-button" onclick="this.openAddPlantDialog()">
          <ha-icon icon="mdi:plus-circle"></ha-icon>
          Add Your First Plant
        </button>
        
        <div class="tips-section">
          <h3 class="tips-title">💡 Pro Tips</h3>
          <ul class="tip-list">
            <li class="tip-item">
              <ha-icon icon="mdi:lightbulb" class="tip-icon"></ha-icon>
              <span>Start with easy plants like Pothos or Snake Plant if you're a beginner</span>
            </li>
            <li class="tip-item">
              <ha-icon icon="mdi:lightbulb" class="tip-icon"></ha-icon>
              <span>Use sensor mode with humidity sensors for automatic monitoring</span>
            </li>
            <li class="tip-item">
              <ha-icon icon="mdi:lightbulb" class="tip-icon"></ha-icon>
              <span>Upload photos of your plants to personalize their cards</span>
            </li>
            <li class="tip-item">
              <ha-icon icon="mdi:lightbulb" class="tip-icon"></ha-icon>
              <span>Set up automations to get notifications when plants need water</span>
            </li>
          </ul>
        </div>
      </div>
    `;

    // Bind methods
    this.openAddPlantDialog = this.openAddPlantDialog.bind(this);
  }

  openAddPlantDialog() {
    // Try to find and trigger the settings card's add plant function
    const settingsCard = document.querySelector('planty-settings-card');
    if (settingsCard && settingsCard.openAddPlantModal) {
      settingsCard.openAddPlantModal();
    } else {
      // Fallback: fire a custom event that the dashboard can listen to
      this.dispatchEvent(new CustomEvent('add-plant-requested', {
        bubbles: true,
        composed: true
      }));
    }
  }

  getCardSize() {
    return 3;
  }

  static getStubConfig() {
    return {};
  }
}

customElements.define('planty-welcome-card', PlantyWelcomeCard);

console.info('Planty Welcome Card loaded');
