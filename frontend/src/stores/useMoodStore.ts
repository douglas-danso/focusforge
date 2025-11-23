import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { moodAPI, analyticsAPI } from '../services/api';
import { ApiError } from '../services/api';

export interface MoodEntry {
  id: string;
  user_id: string;
  mood_score: number; // 1-10
  energy_level: number; // 1-10
  stress_level: number; // 1-10
  notes?: string;
  activities?: string[];
  sleep_hours?: number;
  exercise_minutes?: number;
  created_at: string;
  updated_at: string;
}

export interface MoodInsights {
  average_mood: number;
  mood_trend: 'improving' | 'declining' | 'stable';
  energy_correlation: number;
  stress_correlation: number;
  productivity_correlation: number;
  recommendations: string[];
  best_performing_hours: string[];
  worst_performing_hours: string[];
}

export interface MoodAnalytics {
  daily_averages: Array<{
    date: string;
    mood: number;
    energy: number;
    stress: number;
  }>;
  weekly_trends: Array<{
    week: string;
    average_mood: number;
    mood_variance: number;
  }>;
  correlations: {
    mood_vs_productivity: number;
    mood_vs_sleep: number;
    mood_vs_exercise: number;
  };
}

export interface CreateMoodData {
  mood_score: number;
  energy_level: number;
  stress_level: number;
  notes?: string;
  activities?: string[];
  sleep_hours?: number;
  exercise_minutes?: number;
}

interface MoodState {
  currentMood: MoodEntry | null;
  moodHistory: MoodEntry[];
  insights: MoodInsights | null;
  analytics: MoodAnalytics | null;
  isLoading: boolean;
  error: string | null;
  filters: {
    startDate: string;
    endDate: string;
    period: 'day' | 'week' | 'month' | 'year';
  };
}

interface MoodActions {
  // Basic actions
  setCurrentMood: (mood: MoodEntry | null) => void;
  setMoodHistory: (history: MoodEntry[]) => void;
  setInsights: (insights: MoodInsights | null) => void;
  setAnalytics: (analytics: MoodAnalytics | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  setFilters: (filters: Partial<MoodState['filters']>) => void;
  clearFilters: () => void;
  
  // Mood CRUD
  addMoodEntry: (entry: MoodEntry) => void;
  updateMoodEntry: (id: string, updates: Partial<MoodEntry>) => void;
  deleteMoodEntry: (id: string) => void;
  
  // API methods
  fetchMoodHistory: (params?: any) => Promise<void>;
  fetchMoodInsights: () => Promise<void>;
  fetchMoodAnalytics: (params?: any) => Promise<void>;
  logMood: (moodData: CreateMoodData) => Promise<MoodEntry>;
  updateMoodEntryAPI: (id: string, moodData: Partial<MoodEntry>) => Promise<void>;
  deleteMoodEntryAPI: (id: string) => Promise<void>;
  
  // Analytics and insights
  getMoodTrend: () => 'improving' | 'declining' | 'stable';
  getAverageMood: (days?: number) => number;
  getMoodCorrelation: (factor: 'energy' | 'stress' | 'productivity') => number;
  getProductivityRecommendations: () => string[];
  
  // Filtering and search
  getFilteredMoodHistory: () => MoodEntry[];
  getMoodByDate: (date: string) => MoodEntry | null;
  getMoodByDateRange: (startDate: string, endDate: string) => MoodEntry[];
}

type MoodStore = MoodState & MoodActions;

export const useMoodStore = create<MoodStore>()(
  persist(
    (set, get) => ({
      // Initial state
      currentMood: null,
      moodHistory: [],
      insights: null,
      analytics: null,
      isLoading: false,
      error: null,
      filters: {
        startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 7 days ago
        endDate: new Date().toISOString().split('T')[0], // today
        period: 'week' as const,
      },

      // Basic actions
      setCurrentMood: (mood: MoodEntry | null) => set({ currentMood: mood }),
      setMoodHistory: (history: MoodEntry[]) => set({ moodHistory: history }),
      setInsights: (insights: MoodInsights | null) => set({ insights }),
      setAnalytics: (analytics: MoodAnalytics | null) => set({ analytics }),
      setLoading: (loading: boolean) => set({ isLoading: loading }),
      setError: (error: string | null) => set({ error }),
      clearError: () => set({ error: null }),
      
      setFilters: (filters: Partial<MoodState['filters']>) => 
        set((state) => ({ 
          filters: { ...state.filters, ...filters } 
        })),
      
      clearFilters: () => set({ 
        filters: { 
          startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          endDate: new Date().toISOString().split('T')[0],
          period: 'week' as const
        } 
      }),

      // Mood CRUD
      addMoodEntry: (entry: MoodEntry) => set((state) => ({ 
        moodHistory: [entry, ...state.moodHistory],
        currentMood: entry
      })),
      
      updateMoodEntry: (id: string, updates: Partial<MoodEntry>) => set((state) => ({
        moodHistory: state.moodHistory.map((entry) =>
          entry.id === id ? { ...entry, ...updates } : entry
        ),
        currentMood: state.currentMood?.id === id 
          ? { ...state.currentMood, ...updates }
          : state.currentMood,
      })),
      
      deleteMoodEntry: (id: string) => set((state) => ({
        moodHistory: state.moodHistory.filter((entry) => entry.id !== id),
        currentMood: state.currentMood?.id === id ? null : state.currentMood,
      })),

      // API methods
      fetchMoodHistory: async (params?: any) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await moodAPI.getMoodHistory(params);
          
          if (response.success && response.data) {
            set({ moodHistory: response.data });
          } else {
            throw new Error(response.message || 'Failed to fetch mood history');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to fetch mood history';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      fetchMoodInsights: async () => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await moodAPI.getMoodInsights();
          
          if (response.success && response.data) {
            set({ insights: response.data });
          } else {
            throw new Error(response.message || 'Failed to fetch mood insights');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to fetch mood insights';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      fetchMoodAnalytics: async (params?: any) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await moodAPI.getMoodAnalytics(params);
          
          if (response.success && response.data) {
            set({ analytics: response.data });
          } else {
            throw new Error(response.message || 'Failed to fetch mood analytics');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to fetch mood analytics';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      logMood: async (moodData: CreateMoodData): Promise<MoodEntry> => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await moodAPI.logMood(moodData);
          
          if (response.success && response.data) {
            const newEntry = response.data;
            get().addMoodEntry(newEntry);
            return newEntry;
          } else {
            throw new Error(response.message || 'Failed to log mood');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to log mood';
          
          set({ error: errorMessage });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      updateMoodEntryAPI: async (id: string, moodData: Partial<MoodEntry>) => {
        set({ isLoading: true, error: null });
        
        try {
          // Note: The backend might not have a direct update endpoint for mood entries
          // This would need to be implemented in the backend
          const response = await moodAPI.logMood(moodData as CreateMoodData);
          
          if (response.success && response.data) {
            get().updateMoodEntry(id, response.data);
          } else {
            throw new Error(response.message || 'Failed to update mood entry');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to update mood entry';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      deleteMoodEntryAPI: async (id: string) => {
        set({ isLoading: true, error: null });
        
        try {
          // Note: The backend might not have a delete endpoint for mood entries
          // This would need to be implemented in the backend
          get().deleteMoodEntry(id);
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to delete mood entry';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      // Analytics and insights
      getMoodTrend: () => {
        const { insights } = get();
        return insights?.mood_trend || 'stable';
      },

      getAverageMood: (days: number = 7) => {
        const { moodHistory } = get();
        const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
        
        const recentMoods = moodHistory.filter(entry => 
          new Date(entry.created_at) >= cutoffDate
        );
        
        if (recentMoods.length === 0) return 0;
        
        const total = recentMoods.reduce((sum, entry) => sum + entry.mood_score, 0);
        return total / recentMoods.length;
      },

      getMoodCorrelation: (factor: 'energy' | 'stress' | 'productivity') => {
        const { insights } = get();
        
        switch (factor) {
          case 'energy':
            return insights?.energy_correlation || 0;
          case 'stress':
            return insights?.stress_correlation || 0;
          case 'productivity':
            return insights?.productivity_correlation || 0;
          default:
            return 0;
        }
      },

      getProductivityRecommendations: () => {
        const { insights } = get();
        return insights?.recommendations || [];
      },

      // Filtering and search
      getFilteredMoodHistory: () => {
        const { moodHistory, filters } = get();
        let filtered = moodHistory;

        if (filters.startDate) {
          filtered = filtered.filter(entry => 
            entry.created_at >= filters.startDate
          );
        }

        if (filters.endDate) {
          filtered = filtered.filter(entry => 
            entry.created_at <= filters.endDate
          );
        }

        return filtered;
      },

      getMoodByDate: (date: string) => {
        const { moodHistory } = get();
        return moodHistory.find(entry => 
          entry.created_at.startsWith(date)
        ) || null;
      },

      getMoodByDateRange: (startDate: string, endDate: string) => {
        const { moodHistory } = get();
        return moodHistory.filter(entry => 
          entry.created_at >= startDate && entry.created_at <= endDate
        );
      },
    }),
    {
      name: 'focusforge-mood',
      partialize: (state) => ({
        moodHistory: state.moodHistory,
        filters: state.filters,
      }),
    }
  )
);

// Selectors
export const useCurrentMood = () => useMoodStore((state) => state.currentMood);
export const useMoodHistory = () => useMoodStore((state) => state.moodHistory);
export const useMoodInsights = () => useMoodStore((state) => state.insights);
export const useMoodAnalytics = () => useMoodStore((state) => state.analytics);
export const useMoodLoading = () => useMoodStore((state) => state.isLoading);
export const useMoodError = () => useMoodStore((state) => state.error);
export const useMoodFilters = () => useMoodStore((state) => state.filters);

export const useMoodActions = () => useMoodStore((state) => ({
  setCurrentMood: state.setCurrentMood,
  setMoodHistory: state.setMoodHistory,
  setInsights: state.setInsights,
  setAnalytics: state.setAnalytics,
  setLoading: state.setLoading,
  setError: state.setError,
  clearError: state.clearError,
  setFilters: state.setFilters,
  clearFilters: state.clearFilters,
  addMoodEntry: state.addMoodEntry,
  updateMoodEntry: state.updateMoodEntry,
  deleteMoodEntry: state.deleteMoodEntry,
  fetchMoodHistory: state.fetchMoodHistory,
  fetchMoodInsights: state.fetchMoodInsights,
  fetchMoodAnalytics: state.fetchMoodAnalytics,
  logMood: state.logMood,
  updateMoodEntryAPI: state.updateMoodEntryAPI,
  deleteMoodEntryAPI: state.deleteMoodEntryAPI,
}));

export const useMoodComputed = () => useMoodStore((state) => ({
  getMoodTrend: state.getMoodTrend,
  getAverageMood: state.getAverageMood,
  getMoodCorrelation: state.getMoodCorrelation,
  getProductivityRecommendations: state.getProductivityRecommendations,
  getFilteredMoodHistory: state.getFilteredMoodHistory,
  getMoodByDate: state.getMoodByDate,
  getMoodByDateRange: state.getMoodByDateRange,
}));
