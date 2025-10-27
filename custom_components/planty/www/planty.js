// Planty Custom Cards Main Loader
// This file loads and registers all Planty custom cards

console.info('Loading Planty cards...');

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

// Version info
console.info(
  '%c PLANTY %c 1.0.0 ',
  'color: white; background: #4CAF50; font-weight: 700;',
  'color: #4CAF50; background: white; font-weight: 700;'
);

console.info('Planty cards registered successfully');
