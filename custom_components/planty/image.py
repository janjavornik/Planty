"""Image handling for Planty integration."""
from __future__ import annotations

import logging
import os
import shutil
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEFAULT_IMAGE_SIZE = (300, 300)
SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}


class PlantyImageHandler:
    """Handle image processing for Planty plants."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the image handler."""
        self.hass = hass
        self._www_dir = Path(hass.config.path("www"))
        self._planty_dir = self._www_dir / "planty"
        
        # Ensure planty directory exists
        self._planty_dir.mkdir(parents=True, exist_ok=True)

    async def async_process_uploaded_image(
        self, 
        plant_id: str, 
        image_data: bytes, 
        filename: str | None = None
    ) -> str | None:
        """Process an uploaded image for a plant."""
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = dt_util.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"{plant_id}_{timestamp}.jpg"
            
            # Ensure safe filename
            safe_filename = self._make_safe_filename(filename)
            output_path = self._planty_dir / safe_filename
            
            # Process the image
            processed_image = await self.hass.async_add_executor_job(
                self._process_image_data, image_data
            )
            
            if not processed_image:
                return None
            
            # Save the processed image
            await self.hass.async_add_executor_job(
                processed_image.save, output_path, "JPEG", quality=85
            )
            
            _LOGGER.info("Saved plant image: %s", output_path)
            return f"planty/{safe_filename}"
            
        except Exception as err:
            _LOGGER.error("Failed to process plant image: %s", err)
            return None

    async def async_copy_existing_image(
        self, 
        plant_id: str, 
        source_path: str
    ) -> str | None:
        """Copy an existing image file for a plant."""
        try:
            source = Path(source_path)
            if not source.exists():
                _LOGGER.error("Source image not found: %s", source_path)
                return None
            
            # Generate new filename
            timestamp = dt_util.utcnow().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{plant_id}_{timestamp}.jpg"
            output_path = self._planty_dir / safe_filename
            
            # Load and process the image
            with open(source, "rb") as f:
                image_data = f.read()
            
            processed_image = await self.hass.async_add_executor_job(
                self._process_image_data, image_data
            )
            
            if not processed_image:
                return None
            
            # Save the processed image
            await self.hass.async_add_executor_job(
                processed_image.save, output_path, "JPEG", quality=85
            )
            
            _LOGGER.info("Copied and processed plant image: %s", output_path)
            return f"planty/{safe_filename}"
            
        except Exception as err:
            _LOGGER.error("Failed to copy plant image: %s", err)
            return None

    async def async_delete_plant_image(self, image_path: str) -> bool:
        """Delete a plant image file."""
        try:
            # Remove 'planty/' prefix if present
            if image_path.startswith("planty/"):
                image_path = image_path[7:]
            
            full_path = self._planty_dir / image_path
            
            if full_path.exists():
                await self.hass.async_add_executor_job(full_path.unlink)
                _LOGGER.info("Deleted plant image: %s", full_path)
                return True
            else:
                _LOGGER.warning("Plant image not found for deletion: %s", full_path)
                return False
                
        except Exception as err:
            _LOGGER.error("Failed to delete plant image: %s", err)
            return False

    def _process_image_data(self, image_data: bytes) -> Image.Image | None:
        """Process raw image data (crop and resize)."""
        try:
            # Open the image
            with BytesIO(image_data) as bio:
                image = Image.open(bio)
                image = image.convert("RGB")  # Ensure RGB format
                
                # Auto-orient based on EXIF data
                image = ImageOps.exif_transpose(image)
                
                # Crop to square (center crop)
                image = self._crop_to_square(image)
                
                # Resize to target size
                image = image.resize(DEFAULT_IMAGE_SIZE, Image.Resampling.LANCZOS)
                
                return image
                
        except Exception as err:
            _LOGGER.error("Failed to process image data: %s", err)
            return None

    def _crop_to_square(self, image: Image.Image) -> Image.Image:
        """Crop image to square aspect ratio (center crop)."""
        width, height = image.size
        
        # Calculate crop dimensions
        if width > height:
            # Landscape: crop sides
            crop_size = height
            left = (width - crop_size) // 2
            top = 0
        else:
            # Portrait or square: crop top/bottom
            crop_size = width
            left = 0
            top = (height - crop_size) // 2
        
        # Perform crop
        return image.crop((
            left,
            top, 
            left + crop_size,
            top + crop_size
        ))

    def _make_safe_filename(self, filename: str) -> str:
        """Make a filename safe for filesystem."""
        # Remove path separators and dangerous characters
        safe_name = "".join(c for c in filename if c.isalnum() or c in "._-")
        
        # Ensure it has a safe extension
        if not safe_name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            safe_name += '.jpg'
        
        return safe_name

    def get_plant_image_url(self, image_path: str | None) -> str:
        """Get the URL for a plant image."""
        if not image_path:
            return "/static/images/default_plant.png"  # Fallback
        
        # Handle both full paths and relative paths
        if image_path.startswith("planty/"):
            return f"/local/{image_path}"
        else:
            return f"/local/planty/{image_path}"


async def async_setup_image_handler(hass: HomeAssistant) -> PlantyImageHandler:
    """Set up the image handler for Planty."""
    handler = PlantyImageHandler(hass)
    
    # Store in hass.data for access by other components
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    
    hass.data[DOMAIN]["image_handler"] = handler
    
    return handler


def get_image_handler(hass: HomeAssistant) -> PlantyImageHandler | None:
    """Get the image handler from hass.data."""
    return hass.data.get(DOMAIN, {}).get("image_handler")
