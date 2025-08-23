import { useCallback } from 'react';
import { useUIStore } from '../stores/useUIStore';
import { apiService, ApiError } from '../services/api';

type LoadingKey = 'global' | 'auth' | 'tasks' | 'mood' | 'store' | 'calendar';

export const useApi = () => {
  const { addNotification, setLoading, setError, clearError } = useUIStore();

  // Helper function to handle API calls with consistent error handling
  const apiCall = useCallback(async <T>(
    apiFunction: () => Promise<T>,
    loadingKey: LoadingKey,
    errorKey: string,
    successMessage?: string,
    errorMessage?: string
  ): Promise<T | null> => {
    setLoading(loadingKey, true);
    clearError(errorKey);

    try {
      const result = await apiFunction();
      
      if (successMessage) {
        addNotification({
          type: 'success',
          title: 'Success',
          message: successMessage,
        });
      }
      
      return result;
    } catch (error) {
      const message = errorMessage || 
        (error instanceof ApiError ? error.message : 'An unexpected error occurred');
      
      setError(errorKey, message);
      
      addNotification({
        type: 'error',
        title: 'Error',
        message,
        duration: 6000,
      });
      
      return null;
    } finally {
      setLoading(loadingKey, false);
    }
  }, [addNotification, setLoading, setError, clearError]);

  // Auth API
  const auth = {
    googleCallback: (code: string) => 
      apiCall(
        () => apiService.auth.googleCallback(code),
        'auth',
        'auth',
        'Successfully authenticated!',
        'Authentication failed'
      ),
    
    getCurrentUser: () => 
      apiCall(
        () => apiService.auth.getCurrentUser(),
        'auth',
        'auth',
        undefined,
        'Failed to get user data'
      ),
    
    refreshToken: () => 
      apiCall(
        () => apiService.auth.refreshToken(),
        'auth',
        'auth',
        'Token refreshed successfully',
        'Token refresh failed'
      ),
    
    logout: () => 
      apiCall(
        () => apiService.auth.logout(),
        'auth',
        'auth',
        'Logged out successfully',
        'Logout failed'
      ),
  };

  // Tasks API
  const tasks = {
    getTasks: (params?: any) => 
      apiCall(
        () => apiService.tasks.getTasks(params),
        'tasks',
        'tasks',
        undefined,
        'Failed to fetch tasks'
      ),
    
    getDashboardTasks: () => 
      apiCall(
        () => apiService.tasks.getDashboardTasks(),
        'tasks',
        'tasks',
        undefined,
        'Failed to fetch dashboard tasks'
      ),
    
    getTask: (id: string) => 
      apiCall(
        () => apiService.tasks.getTask(id),
        'tasks',
        'tasks',
        undefined,
        'Failed to fetch task'
      ),
    
    createTask: (taskData: any) => 
      apiCall(
        () => apiService.tasks.createTask(taskData),
        'tasks',
        'tasks',
        'Task created successfully!',
        'Failed to create task'
      ),
    
    updateTask: (id: string, taskData: any) => 
      apiCall(
        () => apiService.tasks.updateTask(id, taskData),
        'tasks',
        'tasks',
        'Task updated successfully!',
        'Failed to update task'
      ),
    
    deleteTask: (id: string) => 
      apiCall(
        () => apiService.tasks.deleteTask(id),
        'tasks',
        'tasks',
        'Task deleted successfully!',
        'Failed to delete task'
      ),
    
    startTaskBlock: (taskId: string, blockId: string) => 
      apiCall(
        () => apiService.tasks.startTaskBlock(taskId, blockId),
        'tasks',
        'tasks',
        'Task block started!',
        'Failed to start task block'
      ),
    
    completeTaskBlock: (taskId: string, blockId: string, proofData?: any) => 
      apiCall(
        () => apiService.tasks.completeTaskBlock(taskId, blockId, proofData),
        'tasks',
        'tasks',
        'Task block completed!',
        'Failed to complete task block'
      ),
    
    getTaskGuidance: (taskId: string) => 
      apiCall(
        () => apiService.tasks.getTaskGuidance(taskId),
        'tasks',
        'tasks',
        undefined,
        'Failed to get task guidance'
      ),
    
    getMotivationalSupport: (taskId: string) => 
      apiCall(
        () => apiService.tasks.getMotivationalSupport(taskId),
        'tasks',
        'tasks',
        undefined,
        'Failed to get motivational support'
      ),
  };

  // Mood API
  const mood = {
    logMood: (moodData: any) => 
      apiCall(
        () => apiService.mood.logMood(moodData),
        'mood',
        'mood',
        'Mood logged successfully!',
        'Failed to log mood'
      ),
    
    getMoodHistory: (params?: any) => 
      apiCall(
        () => apiService.mood.getMoodHistory(params),
        'mood',
        'mood',
        undefined,
        'Failed to fetch mood history'
      ),
    
    getMoodInsights: () => 
      apiCall(
        () => apiService.mood.getMoodInsights(),
        'mood',
        'mood',
        undefined,
        'Failed to fetch mood insights'
      ),
    
    getMoodAnalytics: (params?: any) => 
      apiCall(
        () => apiService.mood.getMoodAnalytics(params),
        'mood',
        'mood',
        undefined,
        'Failed to fetch mood analytics'
      ),
  };

  // Store API
  const store = {
    getStoreItems: () => 
      apiCall(
        () => apiService.store.getStoreItems(),
        'store',
        'store',
        undefined,
        'Failed to fetch store items'
      ),
    
    getUserProfile: () => 
      apiCall(
        () => apiService.store.getUserProfile(),
        'store',
        'store',
        undefined,
        'Failed to fetch user profile'
      ),
    
    getActiveRewards: () => 
      apiCall(
        () => apiService.store.getActiveRewards(),
        'store',
        'store',
        undefined,
        'Failed to fetch active rewards'
      ),
    
    getUserStats: () => 
      apiCall(
        () => apiService.store.getUserStats(),
        'store',
        'store',
        undefined,
        'Failed to fetch user stats'
      ),
    
    getSpendingInsights: () => 
      apiCall(
        () => apiService.store.getSpendingInsights(),
        'store',
        'store',
        undefined,
        'Failed to fetch spending insights'
      ),
    
    getLeaderboard: () => 
      apiCall(
        () => apiService.store.getLeaderboard(),
        'store',
        'store',
        undefined,
        'Failed to fetch leaderboard'
      ),
    
    purchaseItem: (itemName: string) => 
      apiCall(
        () => apiService.store.purchaseItem(itemName),
        'store',
        'store',
        'Item purchased successfully!',
        'Failed to purchase item'
      ),
    
    useReward: (rewardId: string) => 
      apiCall(
        () => apiService.store.useReward(rewardId),
        'store',
        'store',
        'Reward activated successfully!',
        'Failed to activate reward'
      ),
  };

  // Rituals API
  const rituals = {
    getTemplates: () => 
      apiCall(
        () => apiService.rituals.getTemplates(),
        'global',
        'rituals',
        undefined,
        'Failed to fetch ritual templates'
      ),
    
    getUserRituals: () => 
      apiCall(
        () => apiService.rituals.getUserRituals(),
        'global',
        'rituals',
        undefined,
        'Failed to fetch user rituals'
      ),
    
    createRitual: (ritualData: any) => 
      apiCall(
        () => apiService.rituals.createRitual(ritualData),
        'global',
        'rituals',
        'Ritual created successfully!',
        'Failed to create ritual'
      ),
    
    updateRitual: (id: string, ritualData: any) => 
      apiCall(
        () => apiService.rituals.updateRitual(id, ritualData),
        'global',
        'rituals',
        'Ritual updated successfully!',
        'Failed to update ritual'
      ),
    
    deleteRitual: (id: string) => 
      apiCall(
        () => apiService.rituals.deleteRitual(id),
        'global',
        'rituals',
        'Ritual deleted successfully!',
        'Failed to delete ritual'
      ),
    
    executeRitual: (id: string) => 
      apiCall(
        () => apiService.rituals.executeRitual(id),
        'global',
        'rituals',
        'Ritual started successfully!',
        'Failed to start ritual'
      ),
    
    getRitualAnalytics: (id: string) => 
      apiCall(
        () => apiService.rituals.getRitualAnalytics(id),
        'global',
        'rituals',
        undefined,
        'Failed to fetch ritual analytics'
      ),
  };

  // Calendar API
  const calendar = {
    getEvents: (params?: any) => 
      apiCall(
        () => apiService.calendar.getEvents(params),
        'calendar',
        'calendar',
        undefined,
        'Failed to fetch calendar events'
      ),
    
    createEvent: (eventData: any) => 
      apiCall(
        () => apiService.calendar.createEvent(eventData),
        'calendar',
        'calendar',
        'Event created successfully!',
        'Failed to create event'
      ),
    
    updateEvent: (id: string, eventData: any) => 
      apiCall(
        () => apiService.calendar.updateEvent(id, eventData),
        'calendar',
        'calendar',
        'Event updated successfully!',
        'Failed to update event'
      ),
    
    deleteEvent: (id: string) => 
      apiCall(
        () => apiService.calendar.deleteEvent(id),
        'calendar',
        'calendar',
        'Event deleted successfully!',
        'Failed to delete event'
      ),
    
    syncGoogleCalendar: () => 
      apiCall(
        () => apiService.calendar.syncGoogleCalendar(),
        'calendar',
        'calendar',
        'Google Calendar synced successfully!',
        'Failed to sync Google Calendar'
      ),
    
    getSyncStatus: () => 
      apiCall(
        () => apiService.calendar.getSyncStatus(),
        'calendar',
        'calendar',
        undefined,
        'Failed to get sync status'
      ),
  };

  // Analytics API
  const analytics = {
    getProductivityAnalytics: (params?: any) => 
      apiCall(
        () => apiService.analytics.getProductivityAnalytics(params),
        'global',
        'analytics',
        undefined,
        'Failed to fetch productivity analytics'
      ),
    
    getFocusSessionAnalytics: (params?: any) => 
      apiCall(
        () => apiService.analytics.getFocusSessionAnalytics(params),
        'global',
        'analytics',
        undefined,
        'Failed to fetch focus session analytics'
      ),
    
    getMoodCorrelationAnalytics: () => 
      apiCall(
        () => apiService.analytics.getMoodCorrelationAnalytics(),
        'global',
        'analytics',
        undefined,
        'Failed to fetch mood correlation analytics'
      ),
  };

  // Spotify API
  const spotify = {
    getPlaylists: () => 
      apiCall(
        () => apiService.spotify.getPlaylists(),
        'global',
        'spotify',
        undefined,
        'Failed to fetch Spotify playlists'
      ),
    
    searchPlaylists: (query: string) => 
      apiCall(
        () => apiService.spotify.searchPlaylists(query),
        'global',
        'spotify',
        undefined,
        'Failed to search playlists'
      ),
    
    playMusic: (playlistId: string) => 
      apiCall(
        () => apiService.spotify.playMusic(playlistId),
        'global',
        'spotify',
        'Music started successfully!',
        'Failed to start music'
      ),
    
    getCurrentPlayback: () => 
      apiCall(
        () => apiService.spotify.getCurrentPlayback(),
        'global',
        'spotify',
        undefined,
        'Failed to get current playback'
      ),
  };

  // Orchestrator API
  const orchestrator = {
    createEnhancedTask: (taskData: any) => 
      apiCall(
        () => apiService.orchestrator.createEnhancedTask(taskData),
        'tasks',
        'orchestrator',
        'Enhanced task created successfully!',
        'Failed to create enhanced task'
      ),
    
    completeEnhancedTask: (taskId: string, completionData: any) => 
      apiCall(
        () => apiService.orchestrator.completeEnhancedTask(taskId, completionData),
        'tasks',
        'orchestrator',
        'Enhanced task completed successfully!',
        'Failed to complete enhanced task'
      ),
    
    getDailyOptimization: () => 
      apiCall(
        () => apiService.orchestrator.getDailyOptimization(),
        'global',
        'orchestrator',
        undefined,
        'Failed to get daily optimization'
      ),
    
    startFocusSession: (sessionData: any) => 
      apiCall(
        () => apiService.orchestrator.startFocusSession(sessionData),
        'global',
        'orchestrator',
        'Focus session started successfully!',
        'Failed to start focus session'
      ),
    
    getOrchestratorStatus: () => 
      apiCall(
        () => apiService.orchestrator.getOrchestratorStatus(),
        'global',
        'orchestrator',
        undefined,
        'Failed to get orchestrator status'
      ),
  };

  // Health check
  const health = {
    checkHealth: () => 
      apiCall(
        () => apiService.health.checkHealth(),
        'global',
        'health',
        undefined,
        'Health check failed'
      ),
  };

  return {
    auth,
    tasks,
    mood,
    store,
    rituals,
    calendar,
    analytics,
    spotify,
    orchestrator,
    health,
  };
};
