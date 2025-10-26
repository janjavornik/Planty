"""Main entry point for Planty add-on."""
from __future__ import annotations

import asyncio
import logging
import signal
import sys
from typing import Optional

from aiohttp import web

from .api import PlantyAPI
from .config import config
from .plant_manager import PlantManager
from .storage import PlantyStorage, PlantsDatabase

_LOGGER = logging.getLogger(__name__)


class PlantyService:
    """Main Planty service."""
    
    def __init__(self) -> None:
        """Initialize the service."""
        self.storage = PlantyStorage()
        self.plants_db = PlantsDatabase()
        self.plant_manager = PlantManager(self.storage, self.plants_db)
        self.api = PlantyAPI(self.plant_manager)
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        _LOGGER.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.stop())
    
    async def start(self) -> None:
        """Start the service."""
        _LOGGER.info("Starting Planty service...")
        
        try:
            # Start plant manager
            await self.plant_manager.start()
            
            # Start web server
            self.runner = web.AppRunner(self.api.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(self.runner, config.host, config.port)
            await self.site.start()
            
            _LOGGER.info(f"Planty web server started on http://{config.host}:{config.port}")
            _LOGGER.info("Planty service is ready!")
            
        except Exception as err:
            _LOGGER.error(f"Failed to start service: {err}")
            raise
    
    async def stop(self) -> None:
        """Stop the service."""
        _LOGGER.info("Stopping Planty service...")
        
        try:
            # Stop plant manager
            await self.plant_manager.stop()
            
            # Stop web server
            if self.site:
                await self.site.stop()
            
            if self.runner:
                await self.runner.cleanup()
            
            _LOGGER.info("Planty service stopped")
            
        except Exception as err:
            _LOGGER.error(f"Error stopping service: {err}")
        
        finally:
            # Exit the event loop
            loop = asyncio.get_event_loop()
            loop.stop()
    
    async def run(self) -> None:
        """Run the service."""
        await self.start()
        
        try:
            # Keep running until stopped
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()


def setup_logging() -> None:
    """Setup logging configuration."""
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger('aiohttp.access').setLevel(logging.WARNING)
    logging.getLogger('aiohttp.server').setLevel(logging.WARNING)


async def main() -> None:
    """Main entry point."""
    setup_logging()
    
    _LOGGER.info("=" * 50)
    _LOGGER.info("Planty - Plant Watering Manager Add-on")
    _LOGGER.info("Version: 1.0.0")
    _LOGGER.info("=" * 50)
    
    service = PlantyService()
    
    try:
        await service.run()
    except KeyboardInterrupt:
        _LOGGER.info("Received keyboard interrupt")
    except Exception as err:
        _LOGGER.error(f"Unexpected error: {err}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
