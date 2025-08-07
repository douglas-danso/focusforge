"""
FocusForge MCP (Model Context Protocol) Integration Package

This package provides Model Context Protocol integration for FocusForge,
enabling standardized access to AI agents and productivity tools.

Components:
- server: MCP server implementation with tool registry
- client: MCP client for consuming tools and managing sessions  
- config: Configuration and tool schema definitions

Usage:
    from app.mcp.server import MCPServer
    from app.mcp.client import MCPSession
    from app.mcp.config import get_mcp_config
"""

__version__ = "1.0.0"
__author__ = "FocusForge Team"

# Import main components for easy access
try:
    from .server import MCPServer
    from .client import MCPSession, get_mcp_client
    from .config import get_mcp_config
    
    __all__ = [
        "MCPServer",
        "MCPSession", 
        "get_mcp_client",
        "get_mcp_config"
    ]
    
except ImportError as e:
    # Graceful handling if dependencies aren't available
    import logging
    logging.getLogger(__name__).warning(f"Some MCP components unavailable: {e}")
    __all__ = []
