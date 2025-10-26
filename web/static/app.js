// Planty Web Application
class PlantyApp {
    constructor() {
        this.plants = {};
        this.plantTypes = {};
        this.websocket = null;
        this.isConnected = false;
        
        this.init();
    }
    
    async init() {
        this.bindEvents();
        this.connectWebSocket();
        await this.loadPlantTypes();
        await this.loadPlants();
    }
    
    bindEvents() {
        // Add plant button
        document.getElementById('add-plant-btn').addEventListener('click', () => this.openAddPlantModal());
        
        // Add plant form
        document.getElementById('add-plant-form').addEventListener('submit', (e) => this.handleAddPlant(e));
        
        // Watering mode change
        document.getElementById('watering-mode').addEventListener('change', (e) => this.toggleWateringMode(e.target.value));
        
        // Plant type change
        document.getElementById('plant-type').addEventListener('change', (e) => this.handlePlantTypeChange(e.target.value));
        
        // Modal close on background click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        });
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            this.isConnected = true;
        };
        
        this.websocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            // Reconnect after 5 seconds
            setTimeout(() => this.connectWebSocket(), 5000);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'plant_added':
            case 'plant_updated':
            case 'plant_watered':
                this.loadPlants();
                break;
            case 'plant_deleted':
                delete this.plants[data.data.plant_id];
                this.renderPlants();
                this.updateStatusOverview();
                break;
        }
    }
    
    async loadPlantTypes() {
        try {
            const response = await fetch('/api/plant-types');
            const data = await response.json();
            this.plantTypes = data.plant_types || {};
            this.populatePlantTypeSelect();
        } catch (error) {
            console.error('Error loading plant types:', error);
            this.showToast('Failed to load plant types', 'error');
        }
    }
    
    populatePlantTypeSelect() {
        const select = document.getElementById('plant-type');
        select.innerHTML = '<option value="">Select a plant type...</option>';
        
        Object.entries(this.plantTypes).forEach(([key, plant]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = `${plant.name} (${plant.care_level})`;
            select.appendChild(option);
        });
    }
    
    async loadPlants() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/plants');
            const data = await response.json();
            this.plants = data.plants || {};
            this.renderPlants();
            this.updateStatusOverview();
        } catch (error) {
            console.error('Error loading plants:', error);
            this.showToast('Failed to load plants', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    renderPlants() {
        const grid = document.getElementById('plants-grid');
        const emptyState = document.getElementById('empty-state');
        
        if (Object.keys(this.plants).length === 0) {
            grid.style.display = 'none';
            emptyState.style.display = 'block';
            return;
        }
        
        grid.style.display = 'grid';
        emptyState.style.display = 'none';
        
        grid.innerHTML = '';
        
        Object.entries(this.plants).forEach(([plantId, plant]) => {
            const card = this.createPlantCard(plantId, plant);
            grid.appendChild(card);
        });
    }
    
    createPlantCard(plantId, plant) {
        const card = document.createElement('div');
        card.className = 'plant-card';
        card.addEventListener('click', () => this.showPlantDetails(plantId, plant));
        
        const status = this.getPlantStatus(plant);
        const daysUntilWater = this.calculateDaysUntilWater(plant);
        const plantTypeInfo = this.plantTypes[plant.type] || {};
        
        card.innerHTML = `
            <div class="plant-image">
                ${plant.image_path ? 
                    `<img src="${plant.image_path}" alt="${plant.name}">` : 
                    '<i class="mdi mdi-leaf"></i>'
                }
                <div class="plant-status-badge ${status.class}">${status.text}</div>
            </div>
            <div class="plant-info">
                <h3 class="plant-name">${plant.name}</h3>
                <p class="plant-type">${plantTypeInfo.name || plant.type || 'Custom Plant'}</p>
                <div class="plant-stats">
                    <div class="plant-stat">
                        <span class="plant-stat-value">${daysUntilWater}</span>
                        <span class="plant-stat-label">Days Left</span>
                    </div>
                    <div class="plant-stat">
                        <span class="plant-stat-value">${plant.watering_interval || 7}</span>
                        <span class="plant-stat-label">Interval</span>
                    </div>
                    ${plant.watering_mode === 'sensor' && plant.humidity ? `
                        <div class="plant-stat">
                            <span class="plant-stat-value">${plant.humidity}%</span>
                            <span class="plant-stat-label">Humidity</span>
                        </div>
                    ` : ''}
                </div>
                <div class="plant-actions">
                    <button class="btn btn-primary btn-small" onclick="event.stopPropagation(); plantyApp.waterPlant('${plantId}')">
                        <i class="mdi mdi-water"></i>
                        Water
                    </button>
                    <button class="btn btn-secondary btn-small" onclick="event.stopPropagation(); plantyApp.editPlant('${plantId}')">
                        <i class="mdi mdi-pencil"></i>
                        Edit
                    </button>
                </div>
            </div>
        `;
        
        return card;
    }
    
    getPlantStatus(plant) {
        const daysUntilWater = this.calculateDaysUntilWater(plant);
        
        if (daysUntilWater < -2) {
            return { class: 'overdue', text: 'Overdue' };
        } else if (daysUntilWater <= 0) {
            return { class: 'needs-water', text: 'Needs Water' };
        } else {
            return { class: 'healthy', text: 'Healthy' };
        }
    }
    
    calculateDaysUntilWater(plant) {
        if (!plant.last_watered) {
            return 0;
        }
        
        const lastWatered = new Date(plant.last_watered);
        const wateringInterval = plant.watering_interval || 7;
        const nextWatering = new Date(lastWatered.getTime() + wateringInterval * 24 * 60 * 60 * 1000);
        const now = new Date();
        const daysUntil = Math.ceil((nextWatering - now) / (1000 * 60 * 60 * 24));
        
        return daysUntil;
    }
    
    updateStatusOverview() {
        let healthyCount = 0;
        let needsWaterCount = 0;
        let overdueCount = 0;
        
        Object.values(this.plants).forEach(plant => {
            const status = this.getPlantStatus(plant);
            switch (status.class) {
                case 'healthy':
                    healthyCount++;
                    break;
                case 'needs-water':
                    needsWaterCount++;
                    break;
                case 'overdue':
                    overdueCount++;
                    break;
            }
        });
        
        document.getElementById('healthy-count').textContent = healthyCount;
        document.getElementById('needs-water-count').textContent = needsWaterCount;
        document.getElementById('overdue-count').textContent = overdueCount;
    }
    
    openAddPlantModal() {
        const modal = document.getElementById('add-plant-modal');
        modal.classList.add('active');
        document.getElementById('plant-name').focus();
    }
    
    closeAddPlantModal() {
        const modal = document.getElementById('add-plant-modal');
        modal.classList.remove('active');
        document.getElementById('add-plant-form').reset();
        this.toggleWateringMode('manual');
    }
    
    toggleWateringMode(mode) {
        const sensorGroup = document.getElementById('humidity-sensor-group');
        const intervalGroup = document.getElementById('watering-interval-group');
        
        if (mode === 'sensor') {
            sensorGroup.style.display = 'block';
            intervalGroup.style.display = 'none';
        } else {
            sensorGroup.style.display = 'none';
            intervalGroup.style.display = 'block';
        }
    }
    
    handlePlantTypeChange(plantType) {
        if (plantType && this.plantTypes[plantType]) {
            const plantInfo = this.plantTypes[plantType];
            document.getElementById('watering-interval').value = plantInfo.watering_interval || 7;
        }
    }
    
    async handleAddPlant(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const plantData = Object.fromEntries(formData.entries());
        
        // Convert numeric fields
        if (plantData.watering_interval) {
            plantData.watering_interval = parseInt(plantData.watering_interval);
        }
        
        try {
            const response = await fetch('/api/plants', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(plantData),
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showToast('Plant added successfully!', 'success');
                this.closeAddPlantModal();
                
                // Handle image upload if provided
                const imageFile = document.getElementById('plant-image').files[0];
                if (imageFile) {
                    await this.uploadPlantImage(result.plant_id, imageFile);
                }
                
                await this.loadPlants();
            } else {
                this.showToast(result.error || 'Failed to add plant', 'error');
            }
        } catch (error) {
            console.error('Error adding plant:', error);
            this.showToast('Failed to add plant', 'error');
        }
    }
    
    async uploadPlantImage(plantId, imageFile) {
        const formData = new FormData();
        formData.append('image', imageFile);
        
        try {
            const response = await fetch(`/api/plants/${plantId}/image`, {
                method: 'POST',
                body: formData,
            });
            
            if (response.ok) {
                this.showToast('Image uploaded successfully!', 'success');
            } else {
                console.error('Failed to upload image');
            }
        } catch (error) {
            console.error('Error uploading image:', error);
        }
    }
    
    async waterPlant(plantId) {
        try {
            const response = await fetch(`/api/plants/${plantId}/water`, {
                method: 'POST',
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showToast('Plant watered successfully!', 'success');
                await this.loadPlants();
            } else {
                this.showToast(result.error || 'Failed to water plant', 'error');
            }
        } catch (error) {
            console.error('Error watering plant:', error);
            this.showToast('Failed to water plant', 'error');
        }
    }
    
    editPlant(plantId) {
        // TODO: Implement edit functionality
        this.showToast('Edit functionality coming soon!', 'warning');
    }
    
    showPlantDetails(plantId, plant) {
        const modal = document.getElementById('plant-details-modal');
        const title = document.getElementById('plant-details-title');
        const content = document.getElementById('plant-details-content');
        
        title.textContent = plant.name;
        
        const plantTypeInfo = this.plantTypes[plant.type] || {};
        const status = this.getPlantStatus(plant);
        const daysUntilWater = this.calculateDaysUntilWater(plant);
        
        content.innerHTML = `
            <div class="detail-row">
                <span class="detail-label">Plant Type</span>
                <span class="detail-value">${plantTypeInfo.name || plant.type || 'Custom Plant'}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Status</span>
                <span class="detail-value">${status.text}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Days Until Watering</span>
                <span class="detail-value">${daysUntilWater}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Watering Interval</span>
                <span class="detail-value">${plant.watering_interval || 7} days</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Watering Mode</span>
                <span class="detail-value">${plant.watering_mode === 'sensor' ? 'Sensor-based' : 'Manual timer'}</span>
            </div>
            ${plant.last_watered ? `
                <div class="detail-row">
                    <span class="detail-label">Last Watered</span>
                    <span class="detail-value">${new Date(plant.last_watered).toLocaleDateString()}</span>
                </div>
            ` : ''}
            ${plant.humidity_sensor ? `
                <div class="detail-row">
                    <span class="detail-label">Humidity Sensor</span>
                    <span class="detail-value">${plant.humidity_sensor}</span>
                </div>
            ` : ''}
            ${plantTypeInfo.description ? `
                <div class="detail-row">
                    <span class="detail-label">Description</span>
                    <span class="detail-value">${plantTypeInfo.description}</span>
                </div>
            ` : ''}
            <div style="margin-top: 1rem; display: flex; gap: 1rem;">
                <button class="btn btn-primary" onclick="plantyApp.waterPlant('${plantId}'); plantyApp.closePlantDetailsModal();">
                    <i class="mdi mdi-water"></i>
                    Water Plant
                </button>
                <button class="btn btn-danger" onclick="plantyApp.deletePlant('${plantId}')">
                    <i class="mdi mdi-delete"></i>
                    Delete
                </button>
            </div>
        `;
        
        modal.classList.add('active');
    }
    
    closePlantDetailsModal() {
        const modal = document.getElementById('plant-details-modal');
        modal.classList.remove('active');
    }
    
    async deletePlant(plantId) {
        if (!confirm('Are you sure you want to delete this plant?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/plants/${plantId}`, {
                method: 'DELETE',
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showToast('Plant deleted successfully!', 'success');
                this.closePlantDetailsModal();
                await this.loadPlants();
            } else {
                this.showToast(result.error || 'Failed to delete plant', 'error');
            }
        } catch (error) {
            console.error('Error deleting plant:', error);
            this.showToast('Failed to delete plant', 'error');
        }
    }
    
    closeModal(modal) {
        modal.classList.remove('active');
    }
    
    showLoading(show) {
        const loading = document.getElementById('loading');
        if (show) {
            loading.classList.add('active');
        } else {
            loading.classList.remove('active');
        }
    }
    
    showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? 'mdi-check-circle' : 
                    type === 'error' ? 'mdi-alert-circle' : 
                    'mdi-information';
        
        toast.innerHTML = `
            <i class="mdi ${icon}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
}

// Global functions for onclick handlers
window.openAddPlantModal = () => plantyApp.openAddPlantModal();
window.closeAddPlantModal = () => plantyApp.closeAddPlantModal();
window.closePlantDetailsModal = () => plantyApp.closePlantDetailsModal();

// Initialize the app
const plantyApp = new PlantyApp();
