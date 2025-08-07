#!/usr/bin/env python3
"""
MCP Server Startup Script for FocusForge
Starts the Model Context Protocol server with all AI agent tools
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.mcp.server import MCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class MCPServerRunner:
    def __init__(self):
        self.server = None
        self.running = False
        
    async def start_server(self):
        """Start the MCP server"""
        try:
            logger.info("Starting MCP Server for FocusForge...")
            
            # Initialize and start server
            self.server = MCPServer()
            await self.server.start()
            
            self.running = True
            logger.info("MCP Server started successfully!")
            logger.info(f"Available tools: {len(self.server.get_available_tools())}")
            
            # Keep the server running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise
    
    async def stop_server(self):
        """Stop the MCP server"""
        if self.server:
            logger.info("Stopping MCP Server...")
            await self.server.stop()
            self.running = False
            logger.info("MCP Server stopped.")
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

async def main():
    """Main function to run the MCP server"""
    runner = MCPServerRunner()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, runner.handle_shutdown)
    signal.signal(signal.SIGTERM, runner.handle_shutdown)
    
    try:
        await runner.start_server()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        await runner.stop_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown completed")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
