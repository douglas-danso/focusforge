"""
API Request and Response Schemas for FocusForge
Defines Pydantic models for all API endpoints
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


# ===== COMMON ENUMS =====

class ProcessingMode(str, Enum):
    IMMEDIATE = "immediate"
    BACKGROUND = "background"


class ActionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MCPToolCategory(str, Enum):
    AI_AGENTS = "ai_agents"
    TASK_MANAGEMENT = "task_management"
    MOOD_TRACKING = "mood_tracking"
    GAMIFICATION = "gamification"
    INTEGRATIONS = "integrations"


# ===== BASE RESPONSE MODELS =====

class BaseResponse(BaseModel):
    success: bool


class ErrorResponse(BaseResponse):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseResponse):
    success: bool = True
    message: Optional[str] = None


# ===== ORCHESTRATOR SCHEMAS =====

class TaskCreationRequest(BaseModel):
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field("", description="Task description")
    duration_minutes: int = Field(60, description="Estimated duration in minutes")
    priority: Optional[str] = Field("medium", description="Task priority")
    tags: Optional[List[str]] = Field([], description="Task tags")
    auto_breakdown: bool = Field(True, description="Automatically break down the task")
    preferences: Optional[Dict[str, Any]] = Field({}, description="User preferences")


class TaskCreationResponse(BaseResponse):
    task: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    breakdown: Optional[Dict[str, Any]] = None
    planned_actions: int = 0
    user_context_enhanced: bool = False
    similar_tasks_found: int = 0
    processing: ProcessingMode
    user_id: str
    job_id: Optional[str] = None


class TaskCompletionRequest(BaseModel):
    task_id: str = Field(..., description="Task ID")
    block_id: Optional[str] = Field(None, description="Specific block ID if completing a block")
    task_title: Optional[str] = Field("", description="Task title for context")
    task_description: Optional[str] = Field("", description="Task description")
    completion_criteria: Optional[str] = Field("", description="Completion criteria")
    proof_text: Optional[str] = Field("", description="Proof of completion text")
    proof_data: Optional[Dict[str, Any]] = Field({}, description="Additional proof data")


class TaskCompletionResponse(BaseResponse):
    validation: Optional[Dict[str, Any]] = None
    motivation: Optional[Dict[str, Any]] = None
    points_awarded: int = 0
    planned_actions: int = 0
    completion_recorded: bool = False
    processing: ProcessingMode
    user_id: str
    job_id: Optional[str] = None


class DailyOptimizationRequest(BaseModel):
    current_mood: str = Field("neutral", description="Current mood")
    current_challenge: str = Field("", description="Current challenge or obstacle")
    recent_accomplishments: List[str] = Field([], description="Recent accomplishments")
    goals: Optional[List[str]] = Field([], description="Daily goals")
    preferences: Optional[Dict[str, Any]] = Field({}, description="User preferences")


class DailyOptimizationResponse(BaseResponse):
    dashboard: Optional[Dict[str, Any]] = None
    mood_analysis: Optional[Dict[str, Any]] = None
    motivation: Optional[Dict[str, Any]] = None
    planned_actions: int = 0
    executed_actions: int = 0
    optimization_score: float = 0.0
    processing: ProcessingMode
    user_id: str
    job_id: Optional[str] = None


class FocusSessionRequest(BaseModel):
    task_id: Optional[str] = Field(None, description="Associated task ID")
    task_title: Optional[str] = Field("", description="Task title")
    task_description: Optional[str] = Field("", description="Task description")
    task_type: str = Field("general", description="Type of task")
    duration_minutes: int = Field(25, description="Session duration")
    current_mood: str = Field("neutral", description="Current mood")
    time_of_day: str = Field("morning", description="Time of day")
    block_id: Optional[str] = Field(None, description="Task block ID")
    environment_preferences: Optional[Dict[str, Any]] = Field({}, description="Environment preferences")


class FocusSessionResponse(BaseResponse):
    session_started: bool = False
    ritual_suggestion: Optional[Dict[str, Any]] = None
    playlist_started: bool = False
    task_analysis: Optional[Dict[str, Any]] = None
    session_context: Optional[Dict[str, Any]] = None
    user_id: str


class ActionResponse(BaseResponse):
    action_id: str
    action_type: str
    priority: str
    status: ActionStatus
    user_id: str
    parameters: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    scheduled_at: Optional[datetime] = None
    attempts: int = 0
    max_attempts: int = 3
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None


class UserActionsResponse(BaseResponse):
    user_id: str
    actions: List[ActionResponse]
    count: int
    status_filter: Optional[str] = None


class ExecuteActionsResponse(BaseResponse):
    user_id: str
    executed_actions: List[Dict[str, Any]]
    count: int


class ChainExecutionRequest(BaseModel):
    chain_input: Dict[str, Any] = Field(..., description="Input data for the chain")
    use_cache: bool = Field(True, description="Whether to use cached results")


class ChainExecutionResponse(BaseResponse):
    chain: str
    user_id: str
    result: Dict[str, Any]
    cached: bool = False


class ChainSequenceRequest(BaseModel):
    chain_specs: List[Dict[str, Any]] = Field(..., description="List of chain specifications")


class ChainSequenceResponse(BaseResponse):
    user_id: str
    chain_count: int
    results: List[Dict[str, Any]]


class UserContextResponse(BaseResponse):
    user_id: str
    context: Dict[str, Any]


class UserContextUpdateRequest(BaseModel):
    context_updates: Dict[str, Any] = Field(..., description="Context updates to apply")


class TaskInsightsResponse(BaseResponse):
    user_id: str
    task_id: str
    insights: Dict[str, Any]


class SimilarTasksResponse(BaseResponse):
    user_id: str
    query: str
    similar_tasks: List[Dict[str, Any]]
    count: int


class BackgroundTaskStatusResponse(BaseResponse):
    job_id: str
    status: Dict[str, Any]


class OrchestratorStatusResponse(BaseResponse):
    status: Dict[str, Any]
    timestamp: datetime


class QueueEventRequest(BaseModel):
    event_type: str = Field(..., description="Type of event")
    event_data: Dict[str, Any] = Field(..., description="Event data")


class QueueEventResponse(BaseResponse):
    message: str
    event_type: str


# ===== MCP SCHEMAS =====

class MCPToolInfo(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    category: str


class MCPToolsResponse(BaseResponse):
    tools: List[MCPToolInfo]
    tools_by_category: Dict[str, List[MCPToolInfo]]
    tool_count: int


class MCPToolCallRequest(BaseModel):
    parameters: Optional[Dict[str, Any]] = Field({}, description="Tool parameters")


class MCPToolCallResponse(BaseResponse):
    tool: str
    result: Optional[Dict[str, Any]] = None
    timestamp: datetime


class MCPStatusResponse(BaseResponse):
    status: str
    system: str
    initialized: bool
    tools_count: int
    services_available: List[str]
    categories: List[str]
    tools_by_category: Dict[str, List[str]]
    timestamp: datetime


class AITaskBreakdownRequest(BaseModel):
    title: str = Field(..., description="Task title")
    description: str = Field("", description="Task description")
    duration_minutes: int = Field(60, description="Duration in minutes")
    user_context: Optional[Dict[str, Any]] = Field({}, description="User context")


class AIMotivationRequest(BaseModel):
    user_context: Dict[str, Any] = Field(..., description="User context")
    current_mood: str = Field(..., description="Current mood")
    challenge: str = Field("", description="Current challenge")
    completed_tasks: Optional[List[Dict]] = Field([], description="Recently completed tasks")


class AIRitualRequest(BaseModel):
    user_mood: str = Field(..., description="User mood")
    task_type: str = Field(..., description="Task type")
    time_of_day: str = Field(..., description="Time of day")
    preferences: Optional[Dict[str, Any]] = Field({}, description="User preferences")


# ===== COMMON TASK SCHEMAS =====

class TaskInfo(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: str
    estimated_minutes: int
    created_at: datetime
    updated_at: datetime
    blocks: Optional[List[Dict[str, Any]]] = None


class TaskBlock(BaseModel):
    id: str
    task_id: str
    block_number: int
    title: str
    description: Optional[str] = None
    duration_minutes: int
    status: str
    created_at: datetime


class UserProfile(BaseModel):
    user_id: str
    points: int
    level: int
    achievements: List[str]
    total_tasks_completed: int
    current_streak: int


class MoodEntry(BaseModel):
    id: str
    user_id: str
    feeling: str
    intensity: Optional[int] = None
    note: Optional[str] = None
    created_at: datetime


# ===== SPOTIFY INTEGRATION SCHEMAS =====

class SpotifyPlaylistRequest(BaseModel):
    playlist_id: str = Field(..., description="Spotify playlist ID")
    device_id: Optional[str] = Field(None, description="Target device ID")


class SpotifyPlaylistResponse(BaseResponse):
    status: str
    playlist_id: str
    device_id: Optional[str] = None
    user_id: str


# ===== ANALYTICS SCHEMAS =====

class AnalyticsRequest(BaseModel):
    metric_type: str = Field(..., description="Type of analytics metric")
    time_period: str = Field("week", description="Time period for analysis")
    filters: Optional[Dict[str, Any]] = Field({}, description="Additional filters")


class AnalyticsResponse(BaseResponse):
    metric_type: str
    time_period: str
    data: Dict[str, Any]
    insights: Optional[List[str]] = None


# ===== VALIDATION HELPERS =====

def validate_user_id(user_id: str) -> str:
    """Validate user ID format"""
    if not user_id or len(user_id) < 3:
        raise ValueError("Invalid user ID")
    return user_id


def validate_duration(minutes: int) -> int:
    """Validate duration is reasonable"""
    if minutes <= 0 or minutes > 480:  # Max 8 hours
        raise ValueError("Duration must be between 1 and 480 minutes")
    return minutes


# ===== RESPONSE HELPERS =====

def create_error_response(error_message: str, details: Optional[Dict[str, Any]] = None) -> ErrorResponse:
    """Create standardized error response"""
    return ErrorResponse(
        error=error_message,
        details=details,
        timestamp=datetime.now()
    )


def create_success_response(message: str = "Operation completed successfully") -> SuccessResponse:
    """Create standardized success response"""
    return SuccessResponse(
        message=message,
        timestamp=datetime.now()
    )
