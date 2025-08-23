// Core types for FocusForge application

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  auth_provider: 'google';
  google_id: string;
  created_at: string;
  updated_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Task Types
export interface PomodoroBlock {
  id: string;
  task_id: string;
  status: 'pending' | 'in_progress' | 'completed';
  start_time?: string;
  end_time?: string;
  duration: number; // in minutes
  proof_data?: any;
}

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string;
  status: TaskStatus;
  duration_minutes: number;
  break_minutes: number;
  difficulty_score: number;
  category: string;
  priority: TaskPriority;
  deadline?: string;
  estimated_blocks: number;
  blocks_completed: number;
  total_tokens_earned: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  tags: string[];
  agent_guidance?: TaskGuidance;
  procrastination_risk: 'low' | 'medium' | 'high';
  recommended_approach: string;
  suggested_ritual_duration: number;
  pomodoro_blocks?: PomodoroBlock[];
  currency_earned?: number;
  actual_duration?: number;
}

export enum TaskStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export enum TaskPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent'
}

export interface TaskBlock {
  id: string;
  task_id: string;
  user_id: string;
  block_number: number;
  title: string;
  description: string;
  estimated_minutes: number;
  break_minutes: number;
  difficulty_multiplier: number;
  energy_level: 'low' | 'medium' | 'high';
  completion_criteria: string;
  status: 'pending' | 'in_progress' | 'completed';
  started_at?: string;
  completed_at?: string;
  proof_data?: ProofData;
  tokens_earned: number;
  created_at: string;
}

export interface TaskGuidance {
  breakdown: TaskBreakdownItem[];
  motivation: string;
  ritual: RitualSuggestion;
  tips: string[];
  estimated_difficulty: number;
  energy_required: 'low' | 'medium' | 'high';
}

export interface TaskBreakdownItem {
  title: string;
  description: string;
  estimated_minutes: number;
  energy_level: 'low' | 'medium' | 'high';
  completion_criteria: string;
}

// Mood Types
export interface MoodEntry {
  id: string;
  user_id: string;
  mood_rating: number; // 1-10
  energy_level: number; // 1-10
  stress_level: number; // 1-10
  motivation_level: number; // 1-10
  notes?: string;
  context?: MoodContext;
  timestamp: string;
}

export interface MoodContext {
  activity: string;
  location: string;
  weather?: string;
  social_situation?: string;
}

export interface MoodInsights {
  average_mood: number;
  mood_trend: 'improving' | 'stable' | 'declining';
  patterns: MoodPattern[];
  recommendations: string[];
  correlation_with_productivity: number;
}

export interface MoodPattern {
  pattern_type: 'time_of_day' | 'day_of_week' | 'activity_based';
  description: string;
  confidence: number;
  data: Record<string, number>;
}

// Store & Gamification Types
export interface StoreItem {
  name: string;
  cost: number;
  type: 'break' | 'entertainment' | 'food' | 'social' | 'wellness' | 'productivity';
  description: string;
  category: string;
  duration_minutes?: number;
  icon: string;
  popularity?: number;
  special?: boolean;
  spotify_integration?: boolean;
  affordable?: boolean;
  previously_purchased?: boolean;
  recommended?: boolean;
}

export interface UserProfile {
  user_id: string;
  currency: number;
  total_earned: number;
  total_spent: number;
  purchases: Purchase[];
  active_rewards: Reward[];
  preferences: UserPreferences;
  stats: UserStats;
  achievements: Achievement[];
  created_at: string;
  last_updated: string;
}

export interface Purchase {
  item_name: string;
  cost: number;
  purchased_at: string;
  used_at?: string;
}

export interface Reward {
  id: string;
  item_name: string;
  type: string;
  description: string;
  duration_minutes: number;
  expires_at: string;
  expires_soon?: boolean;
}

export interface UserStats {
  level: number;
  streak_days: number;
  tasks_completed: number;
  pomodoros_completed: number;
  total_focus_time: number;
  last_activity: string;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked_at: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  notifications: boolean;
  sound_enabled: boolean;
  favorite_categories: string[];
  default_session_duration: number;
  break_reminders: boolean;
}

// Ritual Types
export interface Ritual {
  id: string;
  user_id?: string;
  name: string;
  description: string;
  category: 'deep_work' | 'energy_boost' | 'calm_centered' | 'creative_flow' | 'custom';
  estimated_duration_minutes: number;
  steps: RitualStep[];
  is_template: boolean;
  usage_count?: number;
  effectiveness_rating?: number;
  created_at: string;
}

export interface RitualStep {
  step_type: 'environment_setup' | 'breathing_exercise' | 'meditation' | 'spotify_playlist' | 'intention_setting' | 'custom_action';
  title: string;
  description: string;
  duration_seconds: number;
  setup_instructions?: string[];
  breathing_pattern?: string;
  meditation_type?: 'breathing' | 'body_scan' | 'mindfulness' | 'focus';
  meditation_voice?: 'calm_male' | 'calm_female' | 'energetic_male' | 'energetic_female';
  spotify_playlist_id?: string;
  custom_instructions?: string;
}

export interface RitualExecution {
  id: string;
  ritual_id: string;
  user_id: string;
  current_step: number;
  total_steps: number;
  started_at: string;
  completed_at?: string;
  effectiveness_rating?: number;
  notes?: string;
  session_context?: Record<string, any>;
}

export interface RitualSuggestion {
  ritual_id: string;
  name: string;
  reason: string;
  estimated_duration: number;
  confidence: number;
}

// Calendar Types
export interface CalendarEvent {
  id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  task_id?: string;
  block_id?: string;
  event_type: 'task_block' | 'break' | 'ritual' | 'external';
  calendar_source: 'focusforge' | 'google';
  google_event_id?: string;
}

export interface CalendarView {
  events: CalendarEvent[];
  productivity_insights: ProductivityInsights;
  availability_slots: AvailabilitySlot[];
}

export interface ProductivityInsights {
  total_focus_time: number;
  completed_blocks: number;
  productivity_score: number;
  peak_hours: string[];
  suggestions: string[];
}

export interface AvailabilitySlot {
  start_time: string;
  end_time: string;
  duration_minutes: number;
  optimal_for: 'deep_work' | 'light_work' | 'break';
}

// Proof Types
export interface ProofData {
  proof_texts: ProofText[];
  proof_files: ProofFile[];
  proof_links: string[];
  completion_notes?: string;
}

export interface ProofText {
  content: string;
  description: string;
}

export interface ProofFile {
  filename: string;
  file_type: string;
  file_size: number;
  file_url: string;
  thumbnail_url?: string;
}

export interface ProofValidation {
  overall_score: number;
  confidence_score: number;
  is_valid: boolean;
  feedback: string;
  improvement_suggestions: string[];
  validation_details: Record<string, any>;
}

// Analytics Types
export interface ProductivityMetrics {
  daily_stats: DailyStats[];
  weekly_summary: WeeklyStats;
  trends: ProductivityTrend[];
  correlations: ProductivityCorrelation[];
}

export interface DailyStats {
  date: string;
  tasks_completed: number;
  total_focus_time: number;
  average_mood: number;
  productivity_score: number;
  sessions_completed: number;
}

export interface WeeklyStats {
  week_start: string;
  total_tasks: number;
  total_focus_time: number;
  average_productivity: number;
  streak_days: number;
  achievements_unlocked: number;
}

export interface ProductivityTrend {
  metric: string;
  direction: 'up' | 'down' | 'stable';
  change_percentage: number;
  period: 'daily' | 'weekly' | 'monthly';
}

export interface ProductivityCorrelation {
  factor: string;
  correlation: number;
  description: string;
  recommendation?: string;
}

// Spotify Types
export interface SpotifyPlaylist {
  id: string;
  name: string;
  description?: string;
  image_url?: string;
  track_count: number;
  is_focus_playlist: boolean;
  categories: string[];
}

export interface SpotifyTrack {
  id: string;
  name: string;
  artist: string;
  album: string;
  duration_ms: number;
  preview_url?: string;
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp: string;
}

export interface PaginatedResponse<T = any> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// UI State Types
export interface UIState {
  theme: 'light' | 'dark' | 'system';
  sidebarOpen: boolean;
  activeModal: string | null;
  loading: Record<string, boolean>;
  errors: Record<string, string | null>;
  notifications: Notification[];
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// Form Types
export interface TaskCreateForm {
  title: string;
  description: string;
  duration_minutes: number;
  category: string;
  priority: TaskPriority;
  deadline?: string;
  tags: string[];
}

export interface MoodLogForm {
  mood_rating: number;
  energy_level: number;
  stress_level: number;
  motivation_level: number;
  notes?: string;
  activity?: string;
  location?: string;
}

export interface RitualCreateForm {
  name: string;
  description: string;
  category: string;
  steps: RitualStep[];
}

// Timer Types
export interface TimerState {
  isRunning: boolean;
  isPaused: boolean;
  timeRemaining: number;
  totalTime: number;
  currentBlock?: TaskBlock;
  currentTask?: Task;
  phase: 'work' | 'break' | 'long_break';
  completedBlocks: number;
}

// Error Types
export interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: Record<string, any>;
}

export interface ValidationError {
  field: string;
  message: string;
}

// Utils Types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type OptionalExcept<T, K extends keyof T> = Partial<T> & Pick<T, K>;

export type RequiredExcept<T, K extends keyof T> = Required<T> & Partial<Pick<T, K>>;
