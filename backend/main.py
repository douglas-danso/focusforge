from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import time
import psutil
import os
from typing import Optional
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.unified_mcp import unified_mcp
from app.core.orchestrator import mcp_orchestrator
from app.core.memory import memory_manager
from app.core.background_tasks import task_scheduler
from app.core.vector_store import vector_store
from app.core.auth import auth_service
from app.core.middleware import AuthenticationMiddleware
from app.core.monitoring import performance_monitor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track request performance metrics"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Track successful request
            performance_monitor.track_request_time(
                endpoint=f"{request.method} {request.url.path}",
                duration=duration,
                status="success"
            )

            # Add performance headers
            response.headers["X-Response-Time"] = f"{duration:.3f}s"

            return response

        except Exception as e:
            duration = time.time() - start_time

            # Track failed request
            performance_monitor.track_request_time(
                endpoint=f"{request.method} {request.url.path}",
                duration=duration,
                status="error",
                error_type=type(e).__name__
            )

            raise


app = FastAPI(
    title="FocusForge API - Memory-Chain-Planner Architecture",
    description="Productivity and focus management API with complete Memory-Chain-Planner architecture using MCP",
    version="3.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
async def startup_event():
    """Initialize the complete Memory-Chain-Planner architecture on startup"""
    
    logging.info("Starting FocusForge with Memory-Chain-Planner architecture...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    logging.info("MongoDB connection established")
    
    # Initialize vector store for semantic memory
    try:
        await vector_store.initialize()
        logging.info("Vector store initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize vector store: {e}")
    
    # Initialize Memory-Chain-Planner Orchestrator (which initializes everything)
    try:
        await mcp_orchestrator.initialize()
        logging.info("Memory-Chain-Planner orchestrator initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize orchestrator: {e}")
    
    # Set up background task scheduler (if Redis available)
    try:
        if task_scheduler.task_manager.is_available():
            task_scheduler.setup_recurring_tasks()
            logging.info("Background task scheduler initialized")
        else:
            logging.warning("Background tasks running in fallback mode (Redis not available)")
    except Exception as e:
        logging.warning(f"Background task setup failed: {e}")
    
    # Start performance monitoring
    try:
        await performance_monitor.start_monitoring()
        logging.info("Performance monitoring started")
    except Exception as e:
        logging.warning(f"Performance monitoring failed to start: {e}")
    
    logging.info("FocusForge backend fully initialized with Memory-Chain-Planner architecture")

@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully shutdown all components"""
    
    logging.info("Shutting down FocusForge backend...")
    
    # Stop performance monitoring
    try:
        await performance_monitor.stop_monitoring()
        logging.info("Performance monitoring stopped")
    except Exception as e:
        logging.warning(f"Error stopping performance monitoring: {e}")
    
    # Shutdown orchestrator (which handles all components)
    try:
        await mcp_orchestrator.shutdown()
        logging.info("Memory-Chain-Planner orchestrator shutdown complete")
    except Exception as e:
        logging.error(f"Orchestrator shutdown error: {e}")
    
    # Close auth service HTTP client
    try:
        await auth_service.close()
        logging.info("Auth service shutdown complete")
    except Exception as e:
        logging.error(f"Error during auth service shutdown: {e}")
    
    # Close MongoDB connection
    await close_mongo_connection()
    logging.info("MongoDB connection closed")
    
    logging.info("FocusForge backend shutdown complete")

# Add authentication middleware
app.add_middleware(AuthenticationMiddleware)

# Add performance monitoring middleware
app.add_middleware(PerformanceMiddleware)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "FocusForge API with Memory-Chain-Planner Architecture",
        "version": "3.0.0",
        "architecture": "Memory-Chain-Planner with Unified MCP",
        "components": [
            "Memory Layer (MongoDB + Vector Store)",
            "Chain Layer (LangChain Chains)",
            "Planner Layer (Intelligent Action Planning)",
            "MCP Adapter Layer (Unified Tool Interface)",
            "Background Task System (RQ/Redis)"
        ],
        "features": [
            "AI Task Decomposition",
            "Intelligent Planning", 
            "Persistent Memory",
            "Background Processing",
            "Mood Tracking & Analytics",
            "Gamification System",
            "Spotify Integration",
            "Calendar Integration",
            "Unified Tool Interface"
        ],
        "endpoints": {
            "api": f"{settings.API_V1_STR}",
            "docs": "/docs",
            "health": "/health",
            "metrics": "/metrics",
            "monitoring": "/api/v1/monitoring",
            "mcp_tools": "/mcp/tools",
            "orchestrator_status": "/orchestrator/status"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with complete Memory-Chain-Planner architecture status"""
    try:
        # Get comprehensive system status from orchestrator
        system_status = await mcp_orchestrator.get_system_status()
        
        # Get vector store status
        vector_store_status = await vector_store.get_statistics()
        
        # Get performance monitoring health
        monitor_summary = performance_monitor.get_health_summary()
        
        overall_health = (
            system_status.get("orchestrator_initialized", False) and
            system_status.get("mcp_system", {}).get("initialized", False) and
            vector_store_status.get("is_initialized", False)
        )
        
        return {
            "status": "healthy" if overall_health else "degraded",
            "timestamp": datetime.now().isoformat(),
            "architecture": "Memory-Chain-Planner with Unified MCP",
            "version": "3.0.0",
            "system_status": system_status,
            "performance_metrics": {
                "total_requests": monitor_summary["total_requests"],
                "error_rate": monitor_summary["error_rate"],
                "uptime_seconds": monitor_summary["uptime_seconds"],
                "response_time_ms": 0,  # Will be calculated per request
            },
            "components": {
                "orchestrator": "healthy" if system_status.get("orchestrator_initialized") else "unhealthy",
                "memory_system": "healthy" if system_status.get("memory_system") else "degraded",
                "mcp_system": "healthy" if system_status.get("mcp_system", {}).get("initialized") else "unhealthy",
                "vector_store": "healthy" if vector_store_status.get("is_initialized") else "unhealthy",
                "background_processing": "healthy" if system_status.get("background_processing") else "degraded",
                "monitoring": monitor_summary["status"],
                "database": "healthy",  # Assuming healthy if we reach this point
                "tools_available": system_status.get("mcp_system", {}).get("tools_count", 0),
                "active_actions": system_status.get("active_actions", 0),
                "background_tasks": system_status.get("background_tasks", 0),
                "vector_embeddings": vector_store_status.get("total_vectors", 0)
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "architecture": "Memory-Chain-Planner with Unified MCP",
            "version": "3.0.0"
        }

@app.get("/orchestrator/status")
async def orchestrator_status():
    """Get detailed orchestrator status"""
    try:
        status = await mcp_orchestrator.get_system_status()
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ===== MONITORING ENDPOINTS =====

@app.get("/health/quick", tags=["monitoring"])
async def quick_health_check():
    """Quick health check for load balancer"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/metrics", tags=["monitoring"])
async def get_performance_metrics():
    """Get comprehensive performance metrics"""
    try:
        return {
            "endpoints": performance_monitor.get_endpoint_stats(),
            "system": performance_monitor.get_system_stats(),
            "counters": performance_monitor.get_counters(),
            "gauges": performance_monitor.get_gauges(),
            "histograms": performance_monitor.get_histograms(),
            "recent_errors": performance_monitor.get_recent_errors(limit=10),
            "health_summary": performance_monitor.get_health_summary(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@app.get("/api/v1/monitoring/health", tags=["monitoring"])
async def api_health_check():
    """API-versioned comprehensive health check"""
    return await health_check()


@app.get("/api/v1/monitoring/metrics", tags=["monitoring"])
async def api_performance_metrics():
    """API-versioned performance metrics"""
    return await get_performance_metrics()


@app.get("/api/v1/monitoring/endpoints", tags=["monitoring"])
async def get_endpoint_metrics(endpoint: Optional[str] = None):
    """Get performance metrics for specific endpoint or all endpoints"""
    try:
        return performance_monitor.get_endpoint_stats(endpoint)
    except Exception as e:
        logger.error(f"Error getting endpoint metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get endpoint metrics")


@app.get("/api/v1/monitoring/system", tags=["monitoring"])
async def get_system_metrics():
    """Get system-level performance metrics"""
    try:
        # Get performance monitor system stats
        perf_stats = performance_monitor.get_system_stats()
        
        # Add additional system information
        system_info = {
            "cpu_count": psutil.cpu_count(),
            "memory_total_mb": psutil.virtual_memory().total / (1024 * 1024),
            "disk_usage": {
                "total_gb": psutil.disk_usage('/').total / (1024**3),
                "used_gb": psutil.disk_usage('/').used / (1024**3),
                "free_gb": psutil.disk_usage('/').free / (1024**3)
            },
            "process_info": {
                "pid": os.getpid(),
                "cpu_percent": psutil.Process().cpu_percent(),
                "memory_mb": psutil.Process().memory_info().rss / (1024 * 1024)
            }
        }
        
        return {
            "performance_stats": perf_stats,
            "system_info": system_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system metrics")


@app.get("/api/v1/monitoring/architecture", tags=["monitoring"])
async def get_architecture_status():
    """Get Memory-Chain-Planner architecture-specific monitoring"""
    try:
        # Get orchestrator status
        orchestrator_status = await mcp_orchestrator.get_system_status()
        
        # Get vector store statistics
        vector_stats = await vector_store.get_statistics()
        
        # Get memory manager status
        memory_stats = {
            "short_term_count": len(memory_manager.short_term_memory),
            "working_memory_count": len(memory_manager.working_memory),
            "episodic_count": len(memory_manager.episodic_memory)
        }
        
        # Get background task status
        task_stats = {
            "scheduler_available": task_scheduler.task_manager.is_available(),
            "active_tasks": 0  # TODO: Get from task scheduler
        }
        
        return {
            "architecture": "Memory-Chain-Planner with Unified MCP",
            "orchestrator": orchestrator_status,
            "vector_store": vector_stats,
            "memory_system": memory_stats,
            "background_tasks": task_stats,
            "unified_mcp": {
                "initialized": unified_mcp.is_initialized() if hasattr(unified_mcp, 'is_initialized') else True,
                "available_tools": unified_mcp.get_available_tools() if hasattr(unified_mcp, 'get_available_tools') else []
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting architecture status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get architecture status")


@app.post("/api/v1/monitoring/reset", tags=["monitoring"])
async def reset_monitoring_stats():
    """Reset all monitoring statistics (admin only)"""
    try:
        performance_monitor.reset_stats()
        return {
            "message": "Monitoring statistics reset successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error resetting monitoring stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset monitoring statistics")


@app.get("/api/v1/monitoring/errors", tags=["monitoring"])
async def get_recent_errors(limit: int = 20):
    """Get recent errors and exceptions"""
    try:
        return {
            "recent_errors": performance_monitor.get_recent_errors(limit=limit),
            "error_summary": {
                "total_errors": sum(performance_monitor.get_counters().get(k, 0) 
                                  for k in performance_monitor.get_counters() 
                                  if k.startswith("errors.")),
                "error_rate": performance_monitor.get_health_summary()["error_rate"]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting recent errors: {e}")
        raise HTTPException(status_code=500, detail="Failed to get error information")


# Global exception handler to track errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with monitoring integration"""
    
    # Track the error
    error_tags = {"type": type(exc).__name__}
    performance_monitor.increment_counter("errors.global", tags=error_tags)
    
    logger.error(
        f"Global exception on {request.method} {request.url}: {exc}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("uvicorn not available - run with: python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
