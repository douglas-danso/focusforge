import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { useAuthStore } from '../stores/useAuthStore';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1';
const API_URL = `${API_BASE_URL}/api/${API_VERSION}`;

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

// Error Types
export class ApiError extends Error {
  constructor(
    public status: number,
    public message: string,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Create axios instance
const createApiInstance = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: API_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor to add auth token
  instance.interceptors.request.use(
    (config) => {
      const token = useAuthStore.getState().token;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor for error handling
  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      return response;
    },
    (error) => {
      if (error.response?.status === 401) {
        // Token expired or invalid, redirect to login
        useAuthStore.getState().logout();
        window.location.href = '/login';
      }
      
      // Create standardized error
      const apiError = new ApiError(
        error.response?.status || 500,
        error.response?.data?.message || error.message || 'An unexpected error occurred',
        error.response?.data?.code,
        error.response?.data?.details
      );
      
      return Promise.reject(apiError);
    }
  );

  return instance;
};

// API instance
const api = createApiInstance();

// Generic API methods
export const apiClient = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    api.get(url, config),
  
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    api.post(url, data, config),
  
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    api.put(url, data, config),
  
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    api.patch(url, data, config),
  
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    api.delete(url, config),
};

// Authentication API
export const authAPI = {
  // Google OAuth callback
  googleCallback: async (code: string): Promise<ApiResponse<{ access_token: string; user: any }>> => {
    const response = await apiClient.post('/auth/google/callback', { code });
    return response.data;
  },

  // Get current user
  getCurrentUser: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  // Refresh token
  refreshToken: async (): Promise<ApiResponse<{ access_token: string }>> => {
    const response = await apiClient.post('/auth/refresh');
    return response.data;
  },

  // Logout
  logout: async (): Promise<ApiResponse> => {
    const response = await apiClient.post('/auth/logout');
    return response.data;
  },
};

// Tasks API
export const tasksAPI = {
  // Get all tasks
  getTasks: async (params?: {
    status?: string;
    priority?: string;
    category?: string;
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<any>> => {
    const response = await apiClient.get('/tasks/', { params });
    return response.data;
  },

  // Get dashboard tasks
  getDashboardTasks: async (): Promise<ApiResponse<any[]>> => {
    const response = await apiClient.get('/tasks/dashboard');
    return response.data;
  },

  // Get single task
  getTask: async (id: string): Promise<ApiResponse<any>> => {
    const response = await apiClient.get(`/tasks/${id}`);
    return response.data;
  },

  // Create task
  createTask: async (taskData: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/tasks/', taskData);
    return response.data;
  },

  // Update task
  updateTask: async (id: string, taskData: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.put(`/tasks/${id}`, taskData);
    return response.data;
  },

  // Delete task
  deleteTask: async (id: string): Promise<ApiResponse> => {
    const response = await apiClient.delete(`/tasks/${id}`);
    return response.data;
  },

  // Start task block
  startTaskBlock: async (taskId: string, blockId: string): Promise<ApiResponse<any>> => {
    const response = await apiClient.post(`/tasks/${taskId}/blocks/${blockId}/start`);
    return response.data;
  },

  // Complete task block
  completeTaskBlock: async (taskId: string, blockId: string, proofData?: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.post(`/tasks/${taskId}/blocks/${blockId}/complete`, { proof_data: proofData });
    return response.data;
  },

  // Get task guidance
  getTaskGuidance: async (taskId: string): Promise<ApiResponse<any>> => {
    const response = await apiClient.get(`/tasks/${taskId}/guidance`);
    return response.data;
  },

  // Get motivational support
  getMotivationalSupport: async (taskId: string): Promise<ApiResponse<any>> => {
    const response = await apiClient.get(`/tasks/${taskId}/motivation`);
    return response.data;
  },
};

// Mood API
export const moodAPI = {
  // Log mood
  logMood: async (moodData: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/mood/log', moodData);
    return response.data;
  },

  // Get mood history
  getMoodHistory: async (params?: {
    start_date?: string;
    end_date?: string;
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<any>> => {
    const response = await apiClient.get('/mood/history', { params });
    return response.data;
  },

  // Get mood insights
  getMoodInsights: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/mood/insights');
    return response.data;
  },

  // Get mood analytics
  getMoodAnalytics: async (params?: {
    period?: 'day' | 'week' | 'month' | 'year';
    start_date?: string;
    end_date?: string;
  }): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/mood/analytics', { params });
    return response.data;
  },
};

// Store & Gamification API
export const storeAPI = {
  // Get store items
  getStoreItems: async (): Promise<ApiResponse<any[]>> => {
    const response = await apiClient.get('/store/items');
    return response.data;
  },

  // Get user profile (currency, stats)
  getUserProfile: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/store/profile');
    return response.data;
  },

  // Purchase item
  purchaseItem: async (itemName: string): Promise<ApiResponse<any>> => {
    const response = await apiClient.post(`/store/purchase/${itemName}`);
    return response.data;
  },

  // Get active rewards
  getActiveRewards: async (): Promise<ApiResponse<any[]>> => {
    const response = await apiClient.get('/store/rewards/active');
    return response.data;
  },

  // Use reward
  useReward: async (rewardId: string): Promise<ApiResponse<any>> => {
    const response = await apiClient.post(`/store/rewards/${rewardId}/use`);
    return response.data;
  },

  // Get user stats
  getUserStats: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/store/stats');
    return response.data;
  },

  // Get spending insights
  getSpendingInsights: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/store/insights/spending');
    return response.data;
  },

  // Get leaderboard
  getLeaderboard: async (): Promise<ApiResponse<any[]>> => {
    const response = await apiClient.get('/store/leaderboard');
    return response.data;
  },
};

// Rituals API
export const ritualsAPI = {
  // Get ritual templates
  getTemplates: async (): Promise<ApiResponse<any[]>> => {
    const response = await apiClient.get('/rituals/templates');
    return response.data;
  },

  // Get user rituals
  getUserRituals: async (): Promise<ApiResponse<any[]>> => {
    const response = await apiClient.get('/rituals/user');
    return response.data;
  },

  // Create ritual
  createRitual: async (ritualData: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/rituals/', ritualData);
    return response.data;
  },

  // Update ritual
  updateRitual: async (id: string, ritualData: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.put(`/rituals/${id}`, ritualData);
    return response.data;
  },

  // Delete ritual
  deleteRitual: async (id: string): Promise<ApiResponse> => {
    const response = await apiClient.delete(`/rituals/${id}`);
    return response.data;
  },

  // Execute ritual
  executeRitual: async (id: string): Promise<ApiResponse<any>> => {
    const response = await apiClient.post(`/rituals/${id}/execute`);
    return response.data;
  },

  // Get ritual analytics
  getRitualAnalytics: async (id: string): Promise<ApiResponse<any>> => {
    const response = await apiClient.get(`/rituals/${id}/analytics`);
    return response.data;
  },
};

// Calendar API
export const calendarAPI = {
  // Get calendar events
  getEvents: async (params?: {
    start_date?: string;
    end_date?: string;
    type?: string;
  }): Promise<ApiResponse<any[]>> => {
    const response = await apiClient.get('/calendar/events', { params });
    return response.data;
  },

  // Create calendar event
  createEvent: async (eventData: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/calendar/events', eventData);
    return response.data;
  },

  // Update calendar event
  updateEvent: async (id: string, eventData: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.put(`/calendar/events/${id}`, eventData);
    return response.data;
  },

  // Delete calendar event
  deleteEvent: async (id: string): Promise<ApiResponse> => {
    const response = await apiClient.delete(`/calendar/events/${id}`);
    return response.data;
  },

  // Sync with Google Calendar
  syncGoogleCalendar: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/calendar/sync');
    return response.data;
  },

  // Get calendar sync status
  getSyncStatus: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/calendar/sync/status');
    return response.data;
  },
};

// Analytics API
export const analyticsAPI = {
  // Get productivity analytics
  getProductivityAnalytics: async (params?: {
    period?: 'day' | 'week' | 'month' | 'year';
    start_date?: string;
    end_date?: string;
  }): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/analytics/productivity', { params });
    return response.data;
  },

  // Get focus session analytics
  getFocusSessionAnalytics: async (params?: {
    period?: 'day' | 'week' | 'month' | 'year';
  }): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/analytics/focus-sessions', { params });
    return response.data;
  },

  // Get mood correlation analytics
  getMoodCorrelationAnalytics: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/analytics/mood-correlation');
    return response.data;
  },
};

// Spotify API
export const spotifyAPI = {
  // Get playlists
  getPlaylists: async (): Promise<ApiResponse<any[]>> => {
    const response = await apiClient.get('/spotify/playlists');
    return response.data;
  },

  // Search playlists
  searchPlaylists: async (query: string): Promise<ApiResponse<any[]>> => {
    const response = await apiClient.get('/spotify/search', { params: { q: query } });
    return response.data;
  },

  // Play music
  playMusic: async (playlistId: string): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/spotify/play', { playlist_id: playlistId });
    return response.data;
  },

  // Get current playback
  getCurrentPlayback: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/spotify/playback');
    return response.data;
  },
};

// Orchestrator API (Memory-Chain-Planner)
export const orchestratorAPI = {
  // Create enhanced task
  createEnhancedTask: async (taskData: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/orchestrator/tasks/create-enhanced', taskData);
    return response.data;
  },

  // Complete enhanced task
  completeEnhancedTask: async (taskId: string, completionData: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.post(`/orchestrator/tasks/complete-enhanced`, {
      task_id: taskId,
      ...completionData,
    });
    return response.data;
  },

  // Get daily optimization
  getDailyOptimization: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/orchestrator/daily-optimization');
    return response.data;
  },

  // Start focus session
  startFocusSession: async (sessionData: any): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/orchestrator/focus-session', sessionData);
    return response.data;
  },

  // Get orchestrator status
  getOrchestratorStatus: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/orchestrator/status');
    return response.data;
  },
};

// Health check
export const healthAPI = {
  checkHealth: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

// Export all APIs
export const apiService = {
  auth: authAPI,
  tasks: tasksAPI,
  mood: moodAPI,
  store: storeAPI,
  rituals: ritualsAPI,
  calendar: calendarAPI,
  analytics: analyticsAPI,
  spotify: spotifyAPI,
  orchestrator: orchestratorAPI,
  health: healthAPI,
};

export default apiService;
