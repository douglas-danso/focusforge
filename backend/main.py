from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.unified_mcp import unified_mcp
from app.core.orchestrator import mcp_orchestrator
from app.core.memory import memory_manager
from app.core.background_tasks import task_scheduler
from app.core.vector_store import vector_store
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    logging.info("FocusForge backend fully initialized with Memory-Chain-Planner architecture")

@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully shutdown all components"""
    
    logging.info("Shutting down FocusForge backend...")
    
    # Shutdown orchestrator (which handles all components)
    try:
        await mcp_orchestrator.shutdown()
        logging.info("Memory-Chain-Planner orchestrator shutdown complete")
    except Exception as e:
        logging.error(f"Orchestrator shutdown error: {e}")
    
    # Close MongoDB connection
    await close_mongo_connection()
    logging.info("MongoDB connection closed")
    
    logging.info("FocusForge backend shutdown complete")

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
            "components": {
                "orchestrator": "healthy" if system_status.get("orchestrator_initialized") else "unhealthy",
                "memory_system": "healthy" if system_status.get("memory_system") else "degraded",
                "mcp_system": "healthy" if system_status.get("mcp_system", {}).get("initialized") else "unhealthy",
                "vector_store": "healthy" if vector_store_status.get("is_initialized") else "unhealthy",
                "background_processing": "healthy" if system_status.get("background_processing") else "degraded",
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
