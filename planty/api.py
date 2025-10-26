"""Web API for Planty."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from aiohttp import web, WSMsgType
from aiohttp.web import Application, Request, Response, WebSocketResponse
import aiohttp_cors
import json

from .plant_manager import PlantManager
from .config import config

_LOGGER = logging.getLogger(__name__)


class PlantyAPI:
    """Web API for Planty."""
    
    def __init__(self, plant_manager: PlantManager) -> None:
        """Initialize the API."""
        self.plant_manager = plant_manager
        self.app = web.Application()
        self.websockets: List[WebSocketResponse] = []
        
        # Setup routes
        self._setup_routes()
        
        # Setup CORS
        self._setup_cors()
    
    def _setup_routes(self) -> None:
        """Setup API routes."""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/api/plants', self.get_plants)
        self.app.router.add_post('/api/plants', self.add_plant)
        self.app.router.add_get('/api/plants/{plant_id}', self.get_plant)
        self.app.router.add_put('/api/plants/{plant_id}', self.update_plant)
        self.app.router.add_delete('/api/plants/{plant_id}', self.delete_plant)
        self.app.router.add_post('/api/plants/{plant_id}/water', self.water_plant)
        self.app.router.add_get('/api/plant-types', self.get_plant_types)
        self.app.router.add_post('/api/plants/{plant_id}/image', self.upload_image)
        self.app.router.add_get('/ws', self.websocket_handler)
    
    def _setup_cors(self) -> None:
        """Setup CORS."""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def health_check(self, request: Request) -> Response:
        """Health check endpoint."""
        return web.json_response({"status": "healthy", "service": "planty"})
    
    async def get_plants(self, request: Request) -> Response:
        """Get all plants."""
        try:
            plants = self.plant_manager.get_all_plants()
            return web.json_response({"plants": plants})
        except Exception as err:
            _LOGGER.error(f"Error getting plants: {err}")
            return web.json_response({"error": str(err)}, status=500)
    
    async def add_plant(self, request: Request) -> Response:
        """Add a new plant."""
        try:
            data = await request.json()
            
            # Validate required fields
            if "plant_name" not in data:
                return web.json_response({"error": "plant_name is required"}, status=400)
            
            plant_id = await self.plant_manager.add_plant(data)
            
            # Notify WebSocket clients
            await self._broadcast_update("plant_added", {"plant_id": plant_id})
            
            return web.json_response({"plant_id": plant_id, "message": "Plant added successfully"})
        
        except Exception as err:
            _LOGGER.error(f"Error adding plant: {err}")
            return web.json_response({"error": str(err)}, status=500)
    
    async def get_plant(self, request: Request) -> Response:
        """Get a specific plant."""
        try:
            plant_id = request.match_info["plant_id"]
            plant = self.plant_manager.get_plant(plant_id)
            
            if not plant:
                return web.json_response({"error": "Plant not found"}, status=404)
            
            return web.json_response({"plant": plant})
        
        except Exception as err:
            _LOGGER.error(f"Error getting plant: {err}")
            return web.json_response({"error": str(err)}, status=500)
    
    async def update_plant(self, request: Request) -> Response:
        """Update a plant."""
        try:
            plant_id = request.match_info["plant_id"]
            data = await request.json()
            
            success = await self.plant_manager.update_plant(plant_id, data)
            
            if not success:
                return web.json_response({"error": "Plant not found"}, status=404)
            
            # Notify WebSocket clients
            await self._broadcast_update("plant_updated", {"plant_id": plant_id})
            
            return web.json_response({"message": "Plant updated successfully"})
        
        except Exception as err:
            _LOGGER.error(f"Error updating plant: {err}")
            return web.json_response({"error": str(err)}, status=500)
    
    async def delete_plant(self, request: Request) -> Response:
        """Delete a plant."""
        try:
            plant_id = request.match_info["plant_id"]
            
            success = await self.plant_manager.remove_plant(plant_id)
            
            if not success:
                return web.json_response({"error": "Plant not found"}, status=404)
            
            # Notify WebSocket clients
            await self._broadcast_update("plant_deleted", {"plant_id": plant_id})
            
            return web.json_response({"message": "Plant deleted successfully"})
        
        except Exception as err:
            _LOGGER.error(f"Error deleting plant: {err}")
            return web.json_response({"error": str(err)}, status=500)
    
    async def water_plant(self, request: Request) -> Response:
        """Water a plant."""
        try:
            plant_id = request.match_info["plant_id"]
            
            success = await self.plant_manager.water_plant(plant_id)
            
            if not success:
                return web.json_response({"error": "Plant not found"}, status=404)
            
            # Notify WebSocket clients
            await self._broadcast_update("plant_watered", {"plant_id": plant_id})
            
            return web.json_response({"message": "Plant watered successfully"})
        
        except Exception as err:
            _LOGGER.error(f"Error watering plant: {err}")
            return web.json_response({"error": str(err)}, status=500)
    
    async def get_plant_types(self, request: Request) -> Response:
        """Get available plant types."""
        try:
            plant_types = self.plant_manager.get_plant_types()
            return web.json_response({"plant_types": plant_types})
        except Exception as err:
            _LOGGER.error(f"Error getting plant types: {err}")
            return web.json_response({"error": str(err)}, status=500)
    
    async def upload_image(self, request: Request) -> Response:
        """Upload plant image."""
        try:
            plant_id = request.match_info["plant_id"]
            
            # Check if plant exists
            plant = self.plant_manager.get_plant(plant_id)
            if not plant:
                return web.json_response({"error": "Plant not found"}, status=404)
            
            reader = await request.multipart()
            field = await reader.next()
            
            if field.name != 'image':
                return web.json_response({"error": "Expected 'image' field"}, status=400)
            
            # Create images directory if it doesn't exist
            os.makedirs(config.image_storage_path, exist_ok=True)
            
            # Save image
            filename = f"{plant_id}.jpg"
            filepath = os.path.join(config.image_storage_path, filename)
            
            with open(filepath, 'wb') as f:
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                    f.write(chunk)
            
            # Update plant with image path
            await self.plant_manager.update_plant(plant_id, {"image_path": f"/images/{filename}"})
            
            # Notify WebSocket clients
            await self._broadcast_update("plant_image_updated", {"plant_id": plant_id})
            
            return web.json_response({"message": "Image uploaded successfully", "image_path": f"/images/{filename}"})
        
        except Exception as err:
            _LOGGER.error(f"Error uploading image: {err}")
            return web.json_response({"error": str(err)}, status=500)
    
    async def websocket_handler(self, request: Request) -> WebSocketResponse:
        """Handle WebSocket connections."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websockets.append(ws)
        _LOGGER.info("WebSocket client connected")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_websocket_message(ws, data)
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({"error": "Invalid JSON"}))
                elif msg.type == WSMsgType.ERROR:
                    _LOGGER.error(f'WebSocket error: {ws.exception()}')
        
        except Exception as err:
            _LOGGER.error(f"WebSocket error: {err}")
        
        finally:
            if ws in self.websockets:
                self.websockets.remove(ws)
            _LOGGER.info("WebSocket client disconnected")
        
        return ws
    
    async def _handle_websocket_message(self, ws: WebSocketResponse, data: Dict[str, Any]) -> None:
        """Handle incoming WebSocket message."""
        message_type = data.get("type")
        
        if message_type == "get_plants":
            plants = self.plant_manager.get_all_plants()
            await ws.send_str(json.dumps({
                "type": "plants_data",
                "data": {"plants": plants}
            }))
        
        elif message_type == "ping":
            await ws.send_str(json.dumps({"type": "pong"}))
        
        else:
            await ws.send_str(json.dumps({"error": f"Unknown message type: {message_type}"}))
    
    async def _broadcast_update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Broadcast update to all WebSocket clients."""
        if not self.websockets:
            return
        
        message = json.dumps({
            "type": event_type,
            "data": data
        })
        
        # Remove closed connections
        active_websockets = []
        for ws in self.websockets:
            if not ws.closed:
                try:
                    await ws.send_str(message)
                    active_websockets.append(ws)
                except Exception as err:
                    _LOGGER.warning(f"Failed to send WebSocket message: {err}")
        
        self.websockets = active_websockets
