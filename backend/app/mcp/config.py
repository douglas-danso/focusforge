"""
MCP Configuration for FocusForge
"""

import os
from typing import Dict, Any

# MCP Server Configuration
MCP_SERVER_CONFIG = {
    "name": "focusforge-mcp",
    "version": "1.0.0",
    "description": "FocusForge MCP Server for agentic productivity tools",
    "capabilities": {
        "tools": True,
        "resources": False,
        "prompts": False
    }
}

# Tool Categories
TOOL_CATEGORIES = {
    "ai_agents": [
        "task_breakdown",
        "task_analysis", 
        "motivation_coach",
        "proof_validation",
        "ritual_suggestion",
        "comprehensive_guidance"
    ],
    "task_management": [
        "create_task",
        "get_user_dashboard",
        "start_task_block",
        "complete_task_block"
    ],
    "mood_tracking": [
        "log_mood",
        "mood_analysis"
    ],
    "gamification": [
        "get_user_profile",
        "purchase_item"
    ],
    "integrations": [
        "get_focus_playlist"
    ]
}

# Environment Configuration
MCP_ENV_CONFIG = {
    "host": os.environ.get("MCP_SERVER_HOST", "localhost"),
    "port": int(os.environ.get("MCP_SERVER_PORT", "3001")),
    "enabled": os.environ.get("MCP_ENABLED", "true").lower() == "true",
    "log_level": os.environ.get("MCP_LOG_LEVEL", "INFO"),
    "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
    "MONGODB_URL": os.environ.get("MONGODB_URL", "mongodb://localhost:27017"),
    "DATABASE_NAME": os.environ.get("DATABASE_NAME", "focusforge"),
    "LOG_LEVEL": os.environ.get("LOG_LEVEL", "INFO")
}

# Tool Definitions with Schemas
TOOL_SCHEMAS = {
    "task_breakdown": {
        "description": "Break down complex tasks into manageable blocks",
        "parameters": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string", "required": False},
            "duration_minutes": {"type": "integer", "required": True},
            "user_context": {"type": "object", "required": False}
        }
    },
    "motivation_coach": {
        "description": "Get personalized motivational support",
        "parameters": {
            "user_id": {"type": "string", "required": True},
            "current_mood": {"type": "string", "required": False},
            "challenge": {"type": "string", "required": False}
        }
    }
}

def get_mcp_config() -> Dict[str, Any]:
    """Get complete MCP configuration"""
    return {
        "server": MCP_SERVER_CONFIG,
        "tools": TOOL_CATEGORIES,
        "environment": MCP_ENV_CONFIG,
        "schemas": TOOL_SCHEMAS
    }
