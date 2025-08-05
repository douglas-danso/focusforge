from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

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

class StoreItem(BaseModel):
    name: str
    cost: int
    type: str
    description: Optional[str] = None

class UserProfile(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    currency: int = 0
    purchases: List[str] = []
    preferences: Dict[str, Any] = {}
    
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
