"""
Enhanced data models for Memory-Chain-Planner architecture
Extends existing schemas with AI-driven features and MCP integration
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum

from app.models.schemas import TaskCreate, MoodLogCreate  # Import existing schemas

class AgentType(str, Enum):
    """Types of AI agents in the system"""
    TASK_BREAKDOWN = "task_breakdown"
    MOTIVATION_COACH = "motivation_coach"  
    TASK_WEIGHTING = "task_weighting"
    PROOF_VERIFICATION = "proof_verification"
    RITUAL_ADVISOR = "ritual_advisor"
    PATTERN_ANALYZER = "pattern_analyzer"
    SCHEDULE_OPTIMIZER = "schedule_optimizer"

class ActionType(str, Enum):
    """Types of planned actions"""
    CREATE_TASK = "create_task"
    BREAKDOWN_TASK = "breakdown_task"
    SCHEDULE_BLOCK = "schedule_block"
    START_RITUAL = "start_ritual"
    PLAY_MUSIC = "play_music"
    LOG_MOOD = "log_mood"
    VALIDATE_PROOF = "validate_proof"
    AWARD_POINTS = "award_points"
    SEND_MOTIVATION = "send_motivation"
    ANALYZE_PATTERNS = "analyze_patterns"

class ActionPriority(str, Enum):
    """Priority levels for actions"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"

class MemoryType(str, Enum):
    """Types of memory storage"""
    SHORT_TERM = "short_term"
    WORKING = "working"
    LONG_TERM = "long_term"
    SEMANTIC = "semantic"

class EnhancedTaskCreate(TaskCreate):
    """Enhanced task creation with AI features"""
    ai_breakdown: bool = Field(default=True, description="Enable AI task breakdown")
    difficulty_estimate: Optional[float] = Field(None, ge=0.5, le=3.0)
    user_skill_level: str = Field(default="intermediate", regex="^(beginner|intermediate|advanced)$")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    preferred_time_slots: Optional[List[str]] = Field(default_factory=list)
    ritual_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)

class TaskBlock(BaseModel):
    """Individual task block with AI insights"""
    block_id: str
    task_id: str
    block_number: int
    title: str
    description: str
    duration_minutes: int = Field(default=25, ge=5, le=120)
    status: str = Field(default="pending")
    difficulty_score: float = Field(default=1.0, ge=0.5, le=3.0)
    energy_level: str = Field(default="medium", regex="^(low|medium|high)$")
    completion_criteria: str
    ai_insights: Optional[Dict[str, Any]] = Field(default_factory=dict)
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    proof_id: Optional[str] = None
    points_awarded: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class AgentResponse(BaseModel):
    """Response from an AI agent"""
    agent_type: AgentType
    success: bool
    response_data: Dict[str, Any]
    confidence_score: float = Field(ge=0.0, le=1.0)
    processing_time_ms: int = Field(ge=0)
    context_used: Optional[Dict[str, Any]] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)

class PlannedAction(BaseModel):
    """Planned action with full context"""
    action_id: str = Field(..., description="Unique action identifier")
    action_type: ActionType
    priority: ActionPriority
    parameters: Dict[str, Any] = Field(default_factory=dict)
    estimated_duration: int = Field(ge=1, description="Duration in minutes")
    dependencies: List[str] = Field(default_factory=list)
    scheduled_time: Optional[datetime] = None
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class MemoryEntry(BaseModel):
    """Memory storage entry"""
    memory_id: str
    memory_type: MemoryType
    user_id: str
    key: str
    value: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    access_count: int = Field(default=0, ge=0)
    last_accessed: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)

class UserPattern(BaseModel):
    """User behavior pattern analysis"""
    user_id: str
    pattern_type: str
    pattern_data: Dict[str, Any]
    confidence_score: float = Field(ge=0.0, le=1.0)
    sample_size: int = Field(ge=1)
    time_period_days: int = Field(ge=1)
    discovered_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)

class MCPToolCall(BaseModel):
    """MCP tool call request"""
    tool_name: str
    adapter_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[str] = None
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    priority: ActionPriority = Field(default=ActionPriority.MEDIUM)

class MCPToolResponse(BaseModel):
    """MCP tool call response"""
    tool_name: str
    adapter_name: str
    success: bool
    result: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: int = Field(ge=0)
    called_at: datetime = Field(default_factory=datetime.now)

class RitualSuggestion(BaseModel):
    """AI-generated ritual suggestion"""
    ritual_id: str
    name: str
    description: str
    duration_minutes: int = Field(ge=1, le=15)
    steps: List[Dict[str, Any]]
    spotify_playlist: Optional[Dict[str, Any]] = None
    effectiveness_score: float = Field(ge=0.0, le=1.0)
    personalization_factors: List[str] = Field(default_factory=list)
    suitable_for: List[str] = Field(default_factory=list)
    created_by_agent: bool = Field(default=True)
    user_id: str
    generated_at: datetime = Field(default_factory=datetime.now)

class ProofSubmission(BaseModel):
    """Task completion proof submission"""
    proof_id: str
    user_id: str
    block_id: str
    proof_type: str = Field(regex="^(text|image|file|screenshot)$")
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    file_urls: List[str] = Field(default_factory=list)
    submitted_at: datetime = Field(default_factory=datetime.now)

class ProofValidation(BaseModel):
    """AI validation of proof submission"""
    validation_id: str
    proof_id: str
    is_valid: bool
    confidence_score: float = Field(ge=0.0, le=1.0)
    validation_reasoning: str
    feedback: str
    suggestions: List[str] = Field(default_factory=list)
    points_awarded: int = Field(default=0, ge=0)
    validated_by: AgentType = Field(default=AgentType.PROOF_VERIFICATION)
    validated_at: datetime = Field(default_factory=datetime.now)

class UserInsights(BaseModel):
    """Comprehensive user insights from AI analysis"""
    user_id: str
    productivity_score: float = Field(ge=0.0, le=10.0)
    task_completion_rate: float = Field(ge=0.0, le=1.0)
    preferred_difficulty_range: List[float] = Field(default_factory=list)
    peak_productivity_hours: List[int] = Field(default_factory=list)
    mood_stability_score: float = Field(ge=0.0, le=1.0)
    procrastination_risk: str = Field(regex="^(low|medium|high)$")
    recommended_strategies: List[str] = Field(default_factory=list)
    learning_style: str = Field(default="balanced")
    focus_duration_optimal: int = Field(default=25, ge=10, le=90)
    break_duration_optimal: int = Field(default=5, ge=3, le=20)
    generated_at: datetime = Field(default_factory=datetime.now)
    confidence_score: float = Field(ge=0.0, le=1.0)

class SystemHealth(BaseModel):
    """System health and performance metrics"""
    status: str = Field(regex="^(healthy|degraded|unhealthy)$")
    components: Dict[str, str] = Field(default_factory=dict)
    metrics: Dict[str, Union[int, float]] = Field(default_factory=dict)
    active_users: int = Field(ge=0)
    pending_actions: int = Field(ge=0)
    memory_usage_mb: float = Field(ge=0)
    response_time_ms: float = Field(ge=0)
    error_rate: float = Field(ge=0.0, le=1.0)
    uptime_hours: float = Field(ge=0)
    checked_at: datetime = Field(default_factory=datetime.now)

class ScheduleOptimization(BaseModel):
    """AI-optimized schedule recommendation"""
    user_id: str
    target_date: datetime
    total_available_hours: float = Field(ge=0)
    scheduled_blocks: List[Dict[str, Any]] = Field(default_factory=list)
    unscheduled_tasks: List[str] = Field(default_factory=list)
    optimization_score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    recommendations: List[str] = Field(default_factory=list)
    calendar_conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)

class EnhancedMoodLog(MoodLogCreate):
    """Enhanced mood logging with AI insights"""
    intensity: int = Field(default=5, ge=1, le=10)
    energy_level: int = Field(default=5, ge=1, le=10)
    focus_level: int = Field(default=5, ge=1, le=10)
    stress_level: int = Field(default=5, ge=1, le=10)
    context_tags: List[str] = Field(default_factory=list)
    triggers: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    weather: Optional[str] = None
    activity_before: Optional[str] = None
    ai_analysis_requested: bool = Field(default=True)

class MoodInsights(BaseModel):
    """AI-generated mood insights"""
    user_id: str
    time_period_days: int = Field(ge=1)
    mood_trend: str = Field(regex="^(improving|stable|declining|volatile)$")
    average_mood: float = Field(ge=1.0, le=10.0)
    mood_variance: float = Field(ge=0.0)
    peak_mood_times: List[str] = Field(default_factory=list)
    low_mood_triggers: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    correlation_with_productivity: float = Field(ge=-1.0, le=1.0)
    suggested_interventions: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)

class EventTrigger(BaseModel):
    """Event that triggers AI processing"""
    event_id: str
    event_type: str
    user_id: str
    event_data: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    priority: ActionPriority = Field(default=ActionPriority.MEDIUM)
    requires_immediate_processing: bool = Field(default=False)
    triggered_at: datetime = Field(default_factory=datetime.now)

class ProcessingResult(BaseModel):
    """Result of event processing through the system"""
    event_id: str
    success: bool
    planned_actions_count: int = Field(ge=0)
    executed_actions_count: int = Field(ge=0)
    pending_actions_count: int = Field(ge=0)
    processing_time_ms: int = Field(ge=0)
    errors: List[str] = Field(default_factory=list)
    insights_generated: List[str] = Field(default_factory=list)
    processed_at: datetime = Field(default_factory=datetime.now)

# Validation functions
@validator('difficulty_estimate')
def validate_difficulty(cls, v):
    if v is not None and not (0.5 <= v <= 3.0):
        raise ValueError('Difficulty must be between 0.5 and 3.0')
    return v

# Response models for API endpoints
class EnhancedTaskResponse(BaseModel):
    """Response for enhanced task creation"""
    success: bool
    task: EnhancedTaskCreate
    ai_breakdown: List[TaskBlock]
    insights: UserInsights
    planned_actions: List[PlannedAction]
    recommendations: List[str]
    processing_time_ms: int

class DashboardResponse(BaseModel):
    """Enhanced dashboard response with AI insights"""
    user_id: str
    current_tasks: List[TaskBlock]
    pending_actions: List[PlannedAction]
    user_insights: UserInsights
    mood_insights: MoodInsights
    schedule_optimization: Optional[ScheduleOptimization] = None
    system_recommendations: List[str]
    generated_at: datetime

class MCPStatusResponse(BaseModel):
    """MCP system status response"""
    enabled: bool
    connected: bool
    mode: str
    available_tools: List[Dict[str, Any]]
    adapters_count: int
    active_sessions: int
    recent_calls: int
    average_response_time_ms: float
    error_rate: float
    last_health_check: datetime

# Export all models for easy importing
__all__ = [
    'AgentType', 'ActionType', 'ActionPriority', 'MemoryType',
    'EnhancedTaskCreate', 'TaskBlock', 'AgentResponse', 'PlannedAction',
    'MemoryEntry', 'UserPattern', 'MCPToolCall', 'MCPToolResponse',
    'RitualSuggestion', 'ProofSubmission', 'ProofValidation',
    'UserInsights', 'SystemHealth', 'ScheduleOptimization',
    'EnhancedMoodLog', 'MoodInsights', 'EventTrigger', 'ProcessingResult',
    'EnhancedTaskResponse', 'DashboardResponse', 'MCPStatusResponse'
]
