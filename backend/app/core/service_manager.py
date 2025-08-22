"""
Service Manager for optimized service initialization and lifecycle management.
Implements singleton pattern with lazy initialization and proper cleanup.
"""

import asyncio
import logging
from typing import Dict, Any, Type, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class ServiceManager:
    """Singleton service manager for lazy initialization and lifecycle management"""
    
    def __init__(self):
        self._services = {}
        self._initialized = set()
        self._lock = asyncio.Lock()
        self._cleanup_callbacks = {}
        self._initialization_times = {}
        
    async def get_service(self, service_name: str, service_class: Type, *args, **kwargs):
        """Get or create service with lazy initialization"""
        if service_name not in self._services:
            async with self._lock:
                if service_name not in self._services:
                    try:
                        start_time = datetime.now()
                        logger.info(f"Initializing service: {service_name}")
                        
                        # Create service instance
                        service = service_class(*args, **kwargs)
                        
                        # Initialize if the service has an initialize method
                        if hasattr(service, 'initialize'):
                            await service.initialize()
                        
                        self._services[service_name] = service
                        self._initialized.add(service_name)
                        
                        # Track initialization time
                        init_duration = (datetime.now() - start_time).total_seconds()
                        self._initialization_times[service_name] = init_duration
                        
                        logger.info(f"Service {service_name} initialized in {init_duration:.2f}s")
                        
                        # Register cleanup callback if service has cleanup method
                        if hasattr(service, 'cleanup') or hasattr(service, 'close'):
                            cleanup_method = getattr(service, 'cleanup', None) or getattr(service, 'close')
                            self._cleanup_callbacks[service_name] = cleanup_method
                        
                    except Exception as e:
                        logger.error(f"Failed to initialize service {service_name}: {e}")
                        raise
        
        return self._services[service_name]
    
    async def get_or_create_service(self, service_name: str, factory: Callable, *args, **kwargs):
        """Get service using a factory function"""
        if service_name not in self._services:
            async with self._lock:
                if service_name not in self._services:
                    try:
                        start_time = datetime.now()
                        logger.info(f"Creating service with factory: {service_name}")
                        
                        service = await factory(*args, **kwargs) if asyncio.iscoroutinefunction(factory) else factory(*args, **kwargs)
                        
                        self._services[service_name] = service
                        self._initialized.add(service_name)
                        
                        init_duration = (datetime.now() - start_time).total_seconds()
                        self._initialization_times[service_name] = init_duration
                        
                        logger.info(f"Service {service_name} created in {init_duration:.2f}s")
                        
                    except Exception as e:
                        logger.error(f"Failed to create service {service_name}: {e}")
                        raise
        
        return self._services[service_name]
    
    def is_initialized(self, service_name: str) -> bool:
        """Check if service is initialized"""
        return service_name in self._initialized
    
    def get_initialized_services(self) -> Dict[str, Any]:
        """Get all initialized services"""
        return {name: service for name, service in self._services.items() 
                if name in self._initialized}
    
    def get_service_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get service initialization statistics"""
        stats = {}
        for service_name in self._initialized:
            stats[service_name] = {
                'initialized': True,
                'initialization_time': self._initialization_times.get(service_name, 0),
                'has_cleanup': service_name in self._cleanup_callbacks
            }
        return stats
    
    async def cleanup_service(self, service_name: str):
        """Cleanup a specific service"""
        if service_name in self._cleanup_callbacks:
            try:
                cleanup_method = self._cleanup_callbacks[service_name]
                if asyncio.iscoroutinefunction(cleanup_method):
                    await cleanup_method()
                else:
                    cleanup_method()
                logger.info(f"Service {service_name} cleaned up successfully")
            except Exception as e:
                logger.error(f"Error cleaning up service {service_name}: {e}")
        
        # Remove from tracking
        self._services.pop(service_name, None)
        self._initialized.discard(service_name)
        self._cleanup_callbacks.pop(service_name, None)
        self._initialization_times.pop(service_name, None)
    
    async def cleanup_all(self):
        """Cleanup all services"""
        logger.info("Starting cleanup of all services")
        
        for service_name in list(self._initialized):
            await self.cleanup_service(service_name)
        
        logger.info("All services cleaned up")
    
    async def restart_service(self, service_name: str, service_class: Type, *args, **kwargs):
        """Restart a specific service"""
        logger.info(f"Restarting service: {service_name}")
        
        # Cleanup existing service
        await self.cleanup_service(service_name)
        
        # Recreate service
        return await self.get_service(service_name, service_class, *args, **kwargs)
    
    def __len__(self):
        """Get number of initialized services"""
        return len(self._initialized)
    
    def __contains__(self, service_name: str):
        """Check if service exists"""
        return service_name in self._services
    
    def __repr__(self):
        """String representation"""
        return f"ServiceManager(services={len(self._initialized)}, initialized={list(self._initialized)})"

# Global service manager instance
service_manager = ServiceManager()

# Convenience functions for common service patterns
async def get_database_service():
    """Get database service (convenience function)"""
    from app.core.database import db_manager
    return await service_manager.get_or_create_service(
        'database',
        lambda: db_manager
    )

async def get_task_service():
    """Get task service (convenience function)"""
    from app.services.task_service import TaskService
    from app.core.database import get_database
    
    db = await get_database()
    return await service_manager.get_service('task_service', TaskService, db)

async def get_store_service():
    """Get store service (convenience function)"""
    from app.services.store_service import StoreService
    from app.core.database import get_database
    
    db = await get_database()
    return await service_manager.get_service('store_service', StoreService, db)

async def get_spotify_service():
    """Get Spotify service (convenience function)"""
    from app.services.spotify_service import SpotifyService
    return await service_manager.get_service('spotify_service', SpotifyService)

async def get_calendar_service():
    """Get calendar service (convenience function)"""
    from app.services.calendar_service import CalendarService
    return await service_manager.get_service('calendar_service', CalendarService)

async def get_llm_service():
    """Get LLM service (convenience function)"""
    from app.services.llm_service import LLMService
    return await service_manager.get_service('llm_service', LLMService)
