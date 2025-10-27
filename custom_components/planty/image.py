"""Image handling for Planty integration."""
from __future__ import annotations

import os
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from PIL import Image

_LOGGER = logging.getLogger(__name__)


class ImageHandler:
    """Handle plant image operations."""
    
    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the image handler."""
        self.hass = hass
        self.www_path = os.path.join(hass.config.config_dir, "www", "planty")
        
        # Ensure directory exists
        os.makedirs(self.www_path, exist_ok=True)
    
    async def process_image(self, image_path: str, plant_id: str) -> str | None:
        """Process and save plant image."""
        try:
            # Open and process image
            def process():
                with Image.open(image_path) as img:
                    # Convert to RGB if necessary
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    
                    # Resize to 300x300 while maintaining aspect ratio
                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    
                    # Create square image with padding if needed
                    if img.size[0] != img.size[1]:
                        size = max(img.size)
                        square_img = Image.new("RGB", (size, size), (255, 255, 255))
                        paste_x = (size - img.size[0]) // 2
                        paste_y = (size - img.size[1]) // 2
                        square_img.paste(img, (paste_x, paste_y))
                        img = square_img
                    
                    # Save processed image
                    output_path = os.path.join(self.www_path, f"{plant_id}.jpg")
                    img.save(output_path, "JPEG", quality=85, optimize=True)
                    
                    return f"/local/planty/{plant_id}.jpg"
            
            return await self.hass.async_add_executor_job(process)
            
        except Exception as err:
            _LOGGER.error("Failed to process image for plant %s: %s", plant_id, err)
            return None


async def async_setup_image_handler(hass: HomeAssistant) -> ImageHandler:
    """Set up the image handler."""
    return ImageHandler(hass)
