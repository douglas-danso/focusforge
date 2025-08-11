"""
Enhanced configuration for Memory-Chain-Planner architecture
Extends existing config with AI, MCP, and orchestrator settings
"""

import os
from typing import Dict, List, Any, Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class EnhancedSettings(BaseSettings):
    """Enhanced settings for FocusForge with Memory-Chain-Planner architecture"""
    
    # Existing core settings (inherit from app.core.config if available)
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FocusForge"
    VERSION: str = "2.0.0"
    
    # Database settings
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://mongo:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "focusforge")
    
    # Redis settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")

    SPOTIPY_CLIENT_ID: str = os.getenv("SPOTIPY_CLIENT_ID", "")
    SPOTIPY_CLIENT_SECRET: str = os.getenv("SPOTIPY_CLIENT_SECRET", "")
    SPOTIPY_REDIRECT_URI: str = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:3000/callback")

    # AI/LLM settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    TEMPERATURE: float = os.getenv("TEMPERATURE", 0.3)
    MAX_TOKENS: int = 2000
    LLM_TIMEOUT_SECONDS: int = 30
    
    # Memory-Chain-Planner settings
    MEMORY_SHORT_TERM_TTL_SECONDS: int = 3600  # 1 hour
    MEMORY_WORKING_TTL_SECONDS: int = 86400    # 24 hours
    MEMORY_CLEANUP_INTERVAL_SECONDS: int = 3600  # 1 hour
    
    # Chain execution settings
    CHAIN_EXECUTION_TIMEOUT_SECONDS: int = 60
    MAX_CHAIN_RETRIES: int = 3
    CHAIN_BATCH_SIZE: int = 5
    
    # Planner settings
    MAX_PENDING_ACTIONS: int = 100
    ACTION_EXECUTION_TIMEOUT_SECONDS: int = 120
    MAX_DAILY_ACTIONS_PER_USER: int = 50
    
    # MCP settings
    MCP_ENABLED: bool = True
    MCP_SERVER_HOST: str = "localhost"
    MCP_SERVER_PORT: int = 3001
    MCP_CONNECTION_TIMEOUT_SECONDS: int = 10
    MCP_CALL_TIMEOUT_SECONDS: int = 30
    MCP_MAX_RETRIES: int = 3
    MCP_RATE_LIMIT_PER_MINUTE: int = 100
    
    # Agent settings
    AGENT_TASK_BREAKDOWN_ENABLED: bool = True
    AGENT_MOTIVATION_COACH_ENABLED: bool = True
    AGENT_TASK_WEIGHTING_ENABLED: bool = True
    AGENT_PROOF_VERIFICATION_ENABLED: bool = True
    AGENT_RITUAL_ADVISOR_ENABLED: bool = True
    AGENT_PATTERN_ANALYZER_ENABLED: bool = True
    AGENT_SCHEDULE_OPTIMIZER_ENABLED: bool = True
    
    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_AI_CALLS_PER_HOUR: int = 100
    RATE_LIMIT_MCP_CALLS_PER_MINUTE: int = 30
    
    # Caching
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 1800  # 30 minutes
    CACHE_MAX_SIZE: int = 1000
    
    # Background processing
    BACKGROUND_TASK_ENABLED: bool = True
    BACKGROUND_TASK_INTERVAL_SECONDS: int = 300  # 5 minutes
    MAX_BACKGROUND_TASKS: int = 10
    
    # Performance settings
    MAX_CONCURRENT_CHAINS: int = 5
    MAX_CONCURRENT_MCP_CALLS: int = 10
    PERFORMANCE_MONITORING_ENABLED: bool = True
    
    # Security settings
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # External service settings
    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""
    GOOGLE_CALENDAR_ENABLED: bool = False
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE_ENABLED: bool = True
    LOG_FILE_PATH: str = "logs/focusforge.log"
    
    # Monitoring and health check settings
    HEALTH_CHECK_ENABLED: bool = True
    METRICS_ENABLED: bool = True
    METRICS_COLLECTION_INTERVAL_SECONDS: int = 60
    
    # Development settings
    DEBUG: bool = False
    TESTING: bool = False
    MOCK_EXTERNAL_SERVICES: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Agent configuration mappings
AGENT_CONFIGS = {
    "task_breakdown": {
        "enabled": True,
        "timeout_seconds": 30,
        "max_retries": 2,
        "cache_results": True,
        "cache_ttl_seconds": 1800
    },
    "motivation_coach": {
        "enabled": True,
        "timeout_seconds": 20,
        "max_retries": 2,
        "cache_results": False,  # Motivation should be fresh
        "cache_ttl_seconds": 0
    },
    "task_weighting": {
        "enabled": True,
        "timeout_seconds": 25,
        "max_retries": 2,
        "cache_results": True,
        "cache_ttl_seconds": 3600
    },
    "proof_verification": {
        "enabled": True,
        "timeout_seconds": 40,
        "max_retries": 1,  # Only one attempt for proof verification
        "cache_results": False,
        "cache_ttl_seconds": 0
    },
    "ritual_advisor": {
        "enabled": True,
        "timeout_seconds": 30,
        "max_retries": 2,
        "cache_results": True,
        "cache_ttl_seconds": 1800
    },
    "pattern_analyzer": {
        "enabled": True,
        "timeout_seconds": 60,
        "max_retries": 2,
        "cache_results": True,
        "cache_ttl_seconds": 3600
    },
    "schedule_optimizer": {
        "enabled": True,
        "timeout_seconds": 45,
        "max_retries": 2,
        "cache_results": True,
        "cache_ttl_seconds": 900  # 15 minutes
    }
}

# MCP Adapter configuration
MCP_ADAPTER_CONFIGS = {
    "task": {
        "rate_limit_per_minute": 30,
        "timeout_seconds": 15,
        "retry_attempts": 3,
        "circuit_breaker_enabled": True
    },
    "calendar": {
        "rate_limit_per_minute": 10,
        "timeout_seconds": 20,
        "retry_attempts": 2,
        "circuit_breaker_enabled": True
    },
    "spotify": {
        "rate_limit_per_minute": 15,
        "timeout_seconds": 10,
        "retry_attempts": 2,
        "circuit_breaker_enabled": False
    },
    "mood": {
        "rate_limit_per_minute": 20,
        "timeout_seconds": 10,
        "retry_attempts": 3,
        "circuit_breaker_enabled": False
    },
    "proof": {
        "rate_limit_per_minute": 10,
        "timeout_seconds": 30,
        "retry_attempts": 1,
        "circuit_breaker_enabled": False
    },
    "gamification": {
        "rate_limit_per_minute": 25,
        "timeout_seconds": 10,
        "retry_attempts": 3,
        "circuit_breaker_enabled": False
    }
}

# Memory configuration
MEMORY_CONFIGS = {
    "short_term": {
        "max_entries": 1000,
        "ttl_seconds": 3600,
        "cleanup_interval_seconds": 300
    },
    "working": {
        "max_entries": 500,
        "ttl_seconds": 86400,
        "cleanup_interval_seconds": 3600
    },
    "long_term": {
        "max_entries": 10000,
        "ttl_seconds": None,  # No expiry
        "cleanup_interval_seconds": 86400
    },
    "semantic": {
        "max_entries": 5000,
        "vector_dimensions": 1536,  # OpenAI embeddings
        "similarity_threshold": 0.7
    }
}

# Action priority mappings for planning
ACTION_PRIORITY_CONFIGS = {
    "critical": {
        "max_delay_seconds": 0,
        "retry_attempts": 5,
        "timeout_multiplier": 2.0
    },
    "high": {
        "max_delay_seconds": 60,
        "retry_attempts": 3,
        "timeout_multiplier": 1.5
    },
    "medium": {
        "max_delay_seconds": 300,
        "retry_attempts": 2,
        "timeout_multiplier": 1.0
    },
    "low": {
        "max_delay_seconds": 900,
        "retry_attempts": 1,
        "timeout_multiplier": 0.5
    },
    "background": {
        "max_delay_seconds": 3600,
        "retry_attempts": 1,
        "timeout_multiplier": 0.3
    }
}

# Feature flags for gradual rollout
FEATURE_FLAGS = {
    "enhanced_task_creation": True,
    "ai_proof_validation": True,
    "mood_pattern_analysis": True,
    "schedule_optimization": True,
    "ritual_suggestions": True,
    "background_processing": True,
    "performance_monitoring": True,
    "semantic_memory": False,  # Experimental
    "advanced_planning": True,
    "user_pattern_learning": True
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "max_response_time_ms": 5000,
    "max_memory_usage_mb": 1024,
    "max_cpu_usage_percent": 80,
    "max_error_rate_percent": 5,
    "min_success_rate_percent": 95
}

# Create settings instance
settings = EnhancedSettings()

# Utility functions
def get_agent_config(agent_name: str) -> Dict[str, Any]:
    """Get configuration for a specific agent"""
    return AGENT_CONFIGS.get(agent_name, {})

def get_mcp_adapter_config(adapter_name: str) -> Dict[str, Any]:
    """Get configuration for a specific MCP adapter"""
    return MCP_ADAPTER_CONFIGS.get(adapter_name, {})

def get_memory_config(memory_type: str) -> Dict[str, Any]:
    """Get configuration for a specific memory type"""
    return MEMORY_CONFIGS.get(memory_type, {})

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return FEATURE_FLAGS.get(feature_name, False)

def get_action_priority_config(priority: str) -> Dict[str, Any]:
    """Get configuration for action priority level"""
    return ACTION_PRIORITY_CONFIGS.get(priority, ACTION_PRIORITY_CONFIGS["medium"])

def validate_performance_threshold(metric_name: str, value: float) -> bool:
    """Check if performance metric is within acceptable threshold"""
    threshold = PERFORMANCE_THRESHOLDS.get(metric_name)
    if threshold is None:
        return True
    
    if metric_name.startswith("max_"):
        return value <= threshold
    elif metric_name.startswith("min_"):
        return value >= threshold
    else:
        return True

# Environment-specific overrides
def apply_environment_overrides():
    """Apply environment-specific configuration overrides"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        settings.DEBUG = False
        settings.LOG_LEVEL = "WARNING"
        settings.MOCK_EXTERNAL_SERVICES = False
        settings.PERFORMANCE_MONITORING_ENABLED = True

    elif env == "testing":
        settings.TESTING = True
        settings.MOCK_EXTERNAL_SERVICES = True
        settings.MCP_ENABLED = False  # Use mocks in testing
        settings.BACKGROUND_TASK_ENABLED = True

    elif env == "development":
        settings.DEBUG = True
        settings.LOG_LEVEL = "DEBUG"
        settings.MOCK_EXTERNAL_SERVICES = True

# Apply overrides when module is imported
apply_environment_overrides()

# Export main settings object
__all__ = ['settings', 'get_agent_config', 'get_mcp_adapter_config', 
          'get_memory_config', 'is_feature_enabled', 'get_action_priority_config',
          'validate_performance_threshold']
