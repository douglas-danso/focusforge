from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# Your existing schemas (keeping them as-is)
class UserBase(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: str = Field(alias="_id")
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    paused = "paused"

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: int = 25
    break_minutes: int = 5

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    duration_minutes: Optional[int] = None
    break_minutes: Optional[int] = None

class Task(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.pending
    duration_minutes: int = 25
    break_minutes: int = 5
    blocks: List[str] = []
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True

class PomodoroSessionCreate(BaseModel):
    task_id: str
    duration_minutes: int = 25

class PomodoroSession(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    task_id: str
    duration_minutes: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    is_completed: bool = False
    
    class Config:
        populate_by_name = True

class MoodLogCreate(BaseModel):
    feeling: str
    note: Optional[str] = ""

class MoodLog(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    feeling: str
    note: Optional[str] = ""
    timestamp: datetime
    
    class Config:
        populate_by_name = True

class SpotifyPlaylistSearch(BaseModel):
    query: str
    limit: int = 5

class SpotifyPlaylistCreate(BaseModel):
    name: str
    public: bool = True
    description: str = ""

class AnalyticsResponse(BaseModel):
    total_sessions: int
    current_streak: int
    best_streak: int
    mood_trends: Dict[str, int]
    weekly_stats: Dict[str, int]
    monthly_stats: Dict[str, int]

# NEW: Enhanced Store and Reward Schemas (additions to your existing system)

# Enums for Store System
class StoreCategory(str, Enum):
    rest = "rest"
    entertainment = "entertainment"
    food = "food"
    social = "social"
    wellness = "wellness"
    productivity = "productivity"
    other = "other"

class TransactionType(str, Enum):
    earning = "earning"
    purchase = "purchase"
    bonus = "bonus"
    refund = "refund"

class EarningSource(str, Enum):
    task_completion = "task_completion"
    pomodoro_completion = "pomodoro_completion"
    streak_bonus = "streak_bonus"
    level_up = "level_up"
    admin_award = "admin_award"

# Enhanced StoreItem (extending your existing one)
class StoreItem(BaseModel):
    name: str
    cost: int
    type: str
    description: Optional[str] = None
    # NEW fields
    category: StoreCategory = StoreCategory.other
    duration_minutes: Optional[int] = None
    spotify_integration: bool = False
    is_active: bool = True
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

class StoreItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    cost: int = Field(..., ge=1, le=10000)
    type: str
    description: str = ""
    category: StoreCategory = StoreCategory.other
    duration_minutes: Optional[int] = Field(None, ge=0, le=1440)
    spotify_integration: bool = False
    metadata: Dict[str, Any] = {}

class StoreItemUpdate(BaseModel):
    name: Optional[str] = None
    cost: Optional[int] = None
    type: Optional[str] = None
    description: Optional[str] = None
    category: Optional[StoreCategory] = None
    duration_minutes: Optional[int] = None
    spotify_integration: Optional[bool] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

# Enhanced UserProfile (extending your existing one)
class UserStats(BaseModel):
    level: int = 1
    total_pomodoros: int = 0
    total_tasks: int = 0
    current_streak: int = 0
    best_streak: int = 0
    last_activity: Optional[datetime] = None

class UserPreferences(BaseModel):
    favorite_categories: List[StoreCategory] = []
    reward_notifications: bool = True
    spotify_auto_play: bool = True
    default_pomodoro_duration: int = 25

class UserProfile(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    currency: int = 0
    purchases: List[str] = []
    preferences: Dict[str, Any] = {}
    # NEW fields for enhanced functionality
    total_earned: int = 0
    total_spent: int = 0
    active_rewards: List[str] = []
    stats: UserStats = UserStats()
    user_preferences: UserPreferences = UserPreferences()
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    
    class Config:
        populate_by_name = True

# NEW: Transaction tracking
class Transaction(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    type: TransactionType
    amount: int  # positive for earnings, negative for purchases
    source: Optional[EarningSource] = None
    item_name: Optional[str] = None
    item_details: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None
    pomodoro_session_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True

# NEW: Reward tracking (for time-based purchases)
class Reward(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    item_name: str
    item_details: StoreItem
    purchased_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime
    used: bool = False
    used_at: Optional[datetime] = None
    notes: str = ""
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at
    
    @property
    def is_available(self) -> bool:
        return not self.used and not self.is_expired
    
    class Config:
        populate_by_name = True

# Request/Response schemas for API endpoints
class PurchaseRequest(BaseModel):
    item_name: str
    notes: str = ""

class PurchaseResponse(BaseModel):
    success: bool
    message: str
    item: Optional[StoreItem] = None
    new_balance: int
    reward_id: Optional[str] = None

class CurrencyAwardRequest(BaseModel):
    user_id: str
    amount: int = Field(..., ge=1)
    source: EarningSource = EarningSource.admin_award
    task_id: Optional[str] = None
    notes: str = ""

class UseRewardRequest(BaseModel):
    reward_id: str
    notes: str = ""

class UseRewardResponse(BaseModel):
    success: bool
    message: str
    reward: Optional[Reward] = None

# Enhanced Analytics (extending your existing AnalyticsResponse)
class EnhancedAnalyticsResponse(BaseModel):
    # Your existing analytics
    total_sessions: int
    current_streak: int
    best_streak: int
    mood_trends: Dict[str, int]
    weekly_stats: Dict[str, int]
    monthly_stats: Dict[str, int]
    
    # NEW: Store and gamification analytics
    user_level: int
    total_currency_earned: int
    total_currency_spent: int
    current_balance: int
    favorite_reward_categories: List[str]
    rewards_purchased: int
    rewards_used: int
    level_progress: Dict[str, Any]  # progress to next level
    spending_breakdown: Dict[str, int]  # by category

# Store management schemas
class StoreFilter(BaseModel):
    category: Optional[StoreCategory] = None
    min_cost: Optional[int] = None
    max_cost: Optional[int] = None
    spotify_integration: Optional[bool] = None
    is_active: bool = True

class StoreSearchRequest(BaseModel):
    query: Optional[str] = None
    filters: StoreFilter = StoreFilter()
    limit: int = Field(20, ge=1, le=100)
    sort_by: str = "name"  # name, cost, category
    sort_desc: bool = False

# Task completion with rewards
class TaskCompletionRequest(BaseModel):
    task_id: str
    proof_type: str = "checkbox"  # checkbox, text, screenshot
    proof_data: Optional[str] = None  # text description or file path
    effort_rating: int = Field(3, ge=1, le=5)  # user's effort rating 1-5

class TaskCompletionResponse(BaseModel):
    success: bool
    message: str
    currency_earned: int
    new_balance: int
    level_up: bool = False
    streak_bonus: int = 0
    task: Task

# Pomodoro completion with rewards
class PomodoroCompletionRequest(BaseModel):
    session_id: str
    mood_after: Optional[str] = None
    notes: Optional[str] = None

class PomodoroCompletionResponse(BaseModel):
    success: bool
    message: str
    currency_earned: int
    new_balance: int
    session: PomodoroSession
    streak_info: Dict[str, Any]

# User stats summary
class UserStatsResponse(BaseModel):
    profile: UserProfile
    recent_activity: Dict[str, Any]
    achievement_progress: Dict[str, Any]
    reward_summary: Dict[str, Any]
    spending_insights: Dict[str, Any]

# Store categories response
class StoreCategoriesResponse(BaseModel):
    categories: List[Dict[str, Any]]  # category name and count
    total_items: int

# Active rewards response
class ActiveRewardsResponse(BaseModel):
    rewards: List[Reward]
    total_count: int
    expiring_soon: List[Reward]  # expiring in next 24 hours

# Migration helpers (to update existing data)
class UserProfileMigration(BaseModel):
    """Helper for migrating existing UserProfile to enhanced version"""
    
    @staticmethod
    def migrate_existing_profile(old_profile: Dict[str, Any]) -> UserProfile:
        """Convert existing profile to enhanced version"""
        return UserProfile(
            id=old_profile.get("_id", ""),
            user_id=old_profile.get("user_id", ""),
            currency=old_profile.get("currency", 0),
            purchases=old_profile.get("purchases", []),
            preferences=old_profile.get("preferences", {}),
            # Set defaults for new fields
            total_earned=old_profile.get("currency", 0),  # Estimate
            total_spent=0,
            active_rewards=[],
            stats=UserStats(),
            user_preferences=UserPreferences(),
            created_at=datetime.now(),
            last_updated=datetime.now()
        )

# Validation helpers
def validate_purchase_power(user_profile: UserProfile, item_cost: int) -> bool:
    """Check if user can afford item"""
    return user_profile.currency >= item_cost

def calculate_task_reward(duration_minutes: int, effort_rating: int, difficulty_multiplier: float = 1.0) -> int:
    """Calculate currency reward for task completion"""
    base_reward = max(1, duration_minutes // 5)
    effort_bonus = effort_rating * 2
    difficulty_bonus = int(base_reward * difficulty_multiplier)
    return base_reward + effort_bonus + difficulty_bonus

def calculate_level_from_earnings(total_earned: int) -> int:
    """Calculate user level based on total earnings"""
    return int((total_earned / 100) ** 0.5) + 1

def get_next_level_threshold(current_level: int) -> int:
    """Get points needed for next level"""
    return (current_level ** 2) * 100

# ===== AGENTIC ARCHITECTURE SCHEMAS =====

class TaskBreakdownBlock(BaseModel):
    """Individual task block from TaskBreakdownAgent"""
    block_number: int
    title: str
    description: str
    estimated_minutes: int
    completion_criteria: str
    energy_level: str  # low, medium, high
    dependencies: List[str] = []

class TaskAnalysis(BaseModel):
    """Analysis from TaskWeightingAgent"""
    difficulty_score: float
    reasoning: str
    complexity_factors: List[str]
    recommended_breaks: int
    energy_type: str  # analytical, creative, physical
    procrastination_risk: str  # low, medium, high
    motivation_tips: List[str]

class ProofValidation(BaseModel):
    """Validation result from ProofVerificationAgent"""
    valid: bool
    confidence_score: float
    reasoning: str
    feedback: str
    suggestions: List[str]

class ProductivityRitual(BaseModel):
    """Ritual suggestion from RitualAdvisorAgent"""
    ritual_name: str
    duration_minutes: int
    steps: List[Dict[str, Any]]
    spotify_suggestion: Optional[Dict[str, str]] = None
    why_this_works: str
    variations: List[str] = []

class AgentGuidance(BaseModel):
    """Comprehensive guidance from all agents"""
    analysis: TaskAnalysis
    breakdown: List[TaskBreakdownBlock]
    motivation: str
    ritual: ProductivityRitual

class AgentRecommendations(BaseModel):
    """High-level recommendations from agent coordination"""
    difficulty_score: float
    recommended_approach: str
    procrastination_risk: str
    suggested_blocks: int
    ritual_duration: int

class ComprehensiveTaskGuidance(BaseModel):
    """Complete response from comprehensive task guidance"""
    success: bool
    guidance: AgentGuidance
    agent_recommendations: AgentRecommendations

class MoodInsights(BaseModel):
    """Enhanced mood insights for agents"""
    current_mood: str
    previous_mood: Optional[str] = None
    recent_trend: str  # improving, declining, stable
    volatility: str    # low, medium, high
    needs_support: bool
    high_energy: bool
    insights: List[str]

class UserContext(BaseModel):
    """User context for agent personalization"""
    skill_level: str
    current_mood: str
    mood_trend: str
    needs_support: bool
    high_energy: bool
    time_of_day: str
    preferences: Dict[str, Any]
    recent_tasks: List[Dict[str, Any]]
    completion_rate: float
    avg_difficulty: float
    total_completed: int
    mood_volatility: str
    recent_moods: List[str]

# Agent request/response schemas
class TaskBreakdownRequest(BaseModel):
    task_data: Dict[str, Any]
    user_context: Optional[UserContext] = None
    detailed: bool = False

class MotivationRequest(BaseModel):
    user_context: UserContext
    mood: str = "neutral"
    challenge: str = ""
    task_history: Optional[List[Dict[str, Any]]] = None

class ProofValidationRequest(BaseModel):
    task_description: str
    proof_text: str
    completion_criteria: str = ""

class RitualRequest(BaseModel):
    mood: str = "neutral"
    task_type: str = "general"
    time_of_day: str = "morning"
    preferences: Dict[str, Any] = {}
    past_rituals: List[Dict[str, Any]] = []

class AgentResponse(BaseModel):
    """Base response for all agent interactions"""
    success: bool
    timestamp: datetime = Field(default_factory=datetime.now)
    error: Optional[str] = None


# ===== CUSTOM RITUAL SCHEMAS =====

class RitualStepType(str, Enum):
    ENVIRONMENT_SETUP = "environment_setup"
    BREATHING_EXERCISE = "breathing_exercise"
    MEDITATION = "meditation"
    SPOTIFY_PLAYLIST = "spotify_playlist"
    INTENTION_SETTING = "intention_setting"
    CUSTOM_ACTION = "custom_action"

class RitualStep(BaseModel):
    step_type: RitualStepType
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    duration_seconds: int = Field(..., ge=10, le=1800)  # 10 seconds to 30 minutes
    
    # Spotify integration
    spotify_playlist_id: Optional[str] = None
    spotify_search_query: Optional[str] = None
    
    # Meditation options
    meditation_type: Optional[str] = Field(None, regex="^(breathing|body_scan|mindfulness|focus)$")
    meditation_voice: Optional[str] = Field(None, regex="^(calm_female|calm_male|energetic_female|energetic_male)$")
    meditation_background: Optional[str] = Field(None, regex="^(nature|rain|ocean|birds|silence)$")
    
    # Breathing exercise options
    breathing_pattern: Optional[str] = Field(None, regex="^(4-4-4-4|4-7-8|breath_of_fire|4-4-6-2)$")
    
    # Environment setup
    setup_instructions: Optional[List[str]] = None
    
    # Custom action
    custom_instructions: Optional[str] = None
    
    @validator('spotify_playlist_id', 'spotify_search_query')
    def validate_spotify_fields(cls, v, values):
        if values.get('step_type') == RitualStepType.SPOTIFY_PLAYLIST:
            if not v and not values.get('spotify_playlist_id') and not values.get('spotify_search_query'):
                raise ValueError('Either spotify_playlist_id or spotify_search_query required for Spotify steps')
        return v
    
    @validator('custom_instructions')
    def validate_custom_instructions(cls, v, values):
        if values.get('step_type') == RitualStepType.CUSTOM_ACTION and not v:
            raise ValueError('custom_instructions required for custom action steps')
        return v

class RitualCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    category: str = Field(..., regex="^(deep_work|energy|calm|creative|study|presentation|custom)$")
    estimated_duration_minutes: int = Field(..., ge=1, le=60)
    steps: List[RitualStep] = Field(..., min_items=1, max_items=10)
    tags: List[str] = Field(default_factory=list, max_items=10)
    is_public: bool = Field(default=False)
    
    @validator('steps')
    def validate_steps(cls, v):
        if len(v) == 0:
            raise ValueError('At least one step is required')
        
        total_duration = sum(step.duration_seconds for step in v)
        if total_duration > 3600:  # Max 1 hour
            raise ValueError('Total ritual duration cannot exceed 1 hour')
        
        return v

class Ritual(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    description: str
    category: str
    estimated_duration_minutes: int
    steps: List[RitualStep]
    tags: List[str]
    is_public: bool
    usage_count: int = 0
    effectiveness_ratings: List[int] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    class Config:
        populate_by_name = True

# ===== MEDITATION SCHEMAS =====

class MeditationType(str, Enum):
    BREATHING = "breathing"
    BODY_SCAN = "body_scan"
    MINDFULNESS = "mindfulness"
    FOCUS = "focus"

class MeditationSessionCreate(BaseModel):
    type: MeditationType = MeditationType.BREATHING
    duration_minutes: int = Field(5, ge=1, le=60)
    guidance_voice: str = Field("calm_female", regex="^(calm_female|calm_male|energetic_female|energetic_male)$")
    background_sound: str = Field("nature", regex="^(nature|rain|ocean|birds|silence)$")
    mood_before: Optional[str] = None

class MeditationSession(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    type: str
    duration_minutes: int
    guidance_voice: str
    background_sound: str
    started_at: datetime
    completed: bool = False
    completed_at: Optional[datetime] = None
    session_notes: str = ""
    mood_before: str = ""
    mood_after: str = ""
    effectiveness_rating: Optional[int] = None
    
    class Config:
        populate_by_name = True

# ===== ENHANCED PROOF SUBMISSION SCHEMAS =====

class ProofType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    LINK = "link"
    VIDEO = "video"

class ProofSubmission(BaseModel):
    proof_type: ProofType
    content: str  # Text content, file path, or URL
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class EnhancedTaskCompletion(BaseModel):
    task_id: str
    block_id: Optional[str] = None
    completion_note: Optional[str] = None
    proofs: List[ProofSubmission] = Field(default_factory=list)
    completion_confidence: int = Field(5, ge=1, le=10)  # Self-assessment
    time_spent_minutes: Optional[int] = None
    challenges_faced: Optional[List[str]] = None
    lessons_learned: Optional[str] = None

# ===== CALENDAR ENHANCEMENT SCHEMAS =====

class CalendarEventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field("", max_length=2000)
    start_time: datetime
    end_time: datetime
    location: Optional[str] = Field(None, max_length=200)
    all_day: bool = False
    recurring: bool = False
    reminder_minutes: int = Field(15, ge=0, le=10080)  # Max 1 week
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class CalendarEvent(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    all_day: bool
    recurring: bool
    reminder_minutes: int
    created_at: datetime
    updated_at: datetime
    google_event_id: Optional[str] = None
    synced_to_google: bool = False
    
    class Config:
        populate_by_name = True