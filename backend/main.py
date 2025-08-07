from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
import uvicorn
import logging

# Import MCP components
try:
    from app.mcp.server import MCPServer
    from app.services.llm_service import LLMService
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP components not available")

app = FastAPI(
    title="FocusForge API",
    description="Productivity and focus management API with MCP integration",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Global MCP server instance (optional)
mcp_server = None

@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB and initialize MCP on startup"""
    global mcp_server
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Initialize MCP integration (optional)
    if MCP_AVAILABLE:
        try:
            # Enable MCP in LLM service
            llm_service = LLMService()
            llm_service.toggle_mcp(True)
            
            logging.info("MCP integration enabled")
        except Exception as e:
            logging.warning(f"Failed to initialize MCP: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection and MCP server on shutdown"""
    global mcp_server
    
    # Close MongoDB connection
    await close_mongo_connection()
    
    # Stop MCP server if running
    if mcp_server:
        try:
            await mcp_server.stop()
            logging.info("MCP server stopped")
        except Exception as e:
            logging.warning(f"Error stopping MCP server: {e}")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "FocusForge API is running",
        "mcp_available": MCP_AVAILABLE,
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    health_status = {"status": "healthy", "database": "connected"}
    
    # Add MCP status if available
    if MCP_AVAILABLE:
        try:
            llm_service = LLMService()
            mcp_status = await llm_service.get_mcp_status()
            health_status["mcp"] = mcp_status
        except Exception as e:
            health_status["mcp"] = {"status": "error", "message": str(e)}
    
    return health_status

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
