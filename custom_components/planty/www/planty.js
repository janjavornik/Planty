// Planty Custom Cards Main Loader
// This file loads and registers all Planty custom cards

import './planty-card.js';
import './planty-header-card.js';
import './planty-settings-card.js';
import './planty-welcome-card.js';

// Version info
console.info(
  '%c PLANTY %c 1.0.0 ',
  'color: white; background: #4CAF50; font-weight: 700;',
  'color: #4CAF50; background: white; font-weight: 700;'
);

// Register card types with Home Assistant
const cardTypes = [
  'planty-card',
  'planty-header-card', 
  'planty-settings-card',
  'planty-welcome-card'
];

// Add to customCards registry
window.customCards = window.customCards || [];
cardTypes.forEach(type => {
  if (!window.customCards.find(card => card.type === type)) {
    window.customCards.push({
      type: type,
      name: type.split('-').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' '),
      description: `Planty ${type.replace('planty-', '').replace('-', ' ')} card`
    });
  }
});

console.info('Planty cards loaded successfully');
