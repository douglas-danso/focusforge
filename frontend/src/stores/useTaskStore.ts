import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { tasksAPI, orchestratorAPI } from '../services/api';
import { ApiError } from '../services/api';
import { Task, TaskStatus, TaskPriority, PomodoroBlock } from '../types';

export interface CreateTaskData {
  title: string;
  description?: string;
  category: string;
  priority?: TaskPriority;
  duration_minutes?: number;
  break_minutes?: number;
  deadline?: string;
  tags?: string[];
}

interface TaskState {
  tasks: Task[];
  currentTask: Task | null;
  isLoading: boolean;
  error: string | null;
  filters: {
    status: string;
    priority: string;
    category: string;
    search: string;
  };
}

interface TaskActions {
  // Basic actions
  setTasks: (tasks: Task[]) => void;
  setCurrentTask: (task: Task | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  setFilters: (filters: Partial<TaskState['filters']>) => void;
  clearFilters: () => void;
  
  // Task CRUD
  addTask: (task: Task) => void;
  updateTask: (id: string, updates: Partial<Task>) => void;
  deleteTask: (id: string) => void;
  
  // API methods
  fetchTasks: (params?: any) => Promise<void>;
  fetchDashboardTasks: () => Promise<void>;
  fetchTask: (id: string) => Promise<void>;
  createTask: (taskData: CreateTaskData) => Promise<Task>;
  updateTaskAPI: (id: string, taskData: Partial<Task>) => Promise<void>;
  deleteTaskAPI: (id: string) => Promise<void>;
  
  // Task operations
  startTaskBlock: (taskId: string, blockId: string) => Promise<void>;
  completeTaskBlock: (taskId: string, blockId: string, proofData?: any) => Promise<void>;
  getTaskGuidance: (taskId: string) => Promise<string>;
  getMotivationalSupport: (taskId: string) => Promise<string>;
  
  // Pomodoro operations
  startPomodoro: (taskId: string, blockId: string) => void;
  pausePomodoro: () => void;
  resumePomodoro: () => void;
  completePomodoro: (proofData?: any) => Promise<void>;
  
  // Filtering and search
  getFilteredTasks: () => Task[];
  getTasksByStatus: (status: string) => Task[];
  getTasksByCategory: (category: string) => Task[];
  searchTasks: (query: string) => Task[];
}

type TaskStore = TaskState & TaskActions;

export const useTaskStore = create<TaskStore>()(
  persist(
    (set, get) => ({
      // Initial state
      tasks: [],
      currentTask: null,
      isLoading: false,
      error: null,
      filters: {
        status: '',
        priority: '',
        category: '',
        search: '',
      },

      // Basic actions
      setTasks: (tasks: Task[]) => set({ tasks }),
      setCurrentTask: (task: Task | null) => set({ currentTask: task }),
      setLoading: (loading: boolean) => set({ isLoading: loading }),
      setError: (error: string | null) => set({ error }),
      clearError: () => set({ error: null }),
      
      setFilters: (filters: Partial<TaskState['filters']>) => 
        set((state) => ({ 
          filters: { ...state.filters, ...filters } 
        })),
      
      clearFilters: () => set({ 
        filters: { status: '', priority: '', category: '', search: '' } 
      }),

      // Task CRUD
      addTask: (task: Task) => set((state) => ({ 
        tasks: [...state.tasks, task] 
      })),
      
      updateTask: (id: string, updates: Partial<Task>) => set((state) => ({
        tasks: state.tasks.map((task) =>
          task.id === id ? { ...task, ...updates } : task
        ),
        currentTask: state.currentTask?.id === id 
          ? { ...state.currentTask, ...updates }
          : state.currentTask,
      })),
      
      deleteTask: (id: string) => set((state) => ({
        tasks: state.tasks.filter((task) => task.id !== id),
        currentTask: state.currentTask?.id === id ? null : state.currentTask,
      })),

      // API methods
      fetchTasks: async (params?: any) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await tasksAPI.getTasks(params);
          
          if (response.success && response.data) {
            set({ tasks: response.data });
          } else {
            throw new Error(response.message || 'Failed to fetch tasks');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to fetch tasks';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      fetchDashboardTasks: async () => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await tasksAPI.getDashboardTasks();
          
          if (response.success && response.data) {
            set({ tasks: response.data });
          } else {
            throw new Error(response.message || 'Failed to fetch dashboard tasks');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to fetch dashboard tasks';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      fetchTask: async (id: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await tasksAPI.getTask(id);
          
          if (response.success && response.data) {
            set({ currentTask: response.data });
          } else {
            throw new Error(response.message || 'Failed to fetch task');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to fetch task';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      createTask: async (taskData: CreateTaskData): Promise<Task> => {
        set({ isLoading: true, error: null });
        
        try {
          // Use orchestrator for enhanced task creation
          const response = await orchestratorAPI.createEnhancedTask(taskData);
          
          if (response.success && response.data) {
            const newTask = response.data;
            get().addTask(newTask);
            return newTask;
          } else {
            throw new Error(response.message || 'Failed to create task');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to create task';
          
          set({ error: errorMessage });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      updateTaskAPI: async (id: string, taskData: Partial<Task>) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await tasksAPI.updateTask(id, taskData);
          
          if (response.success && response.data) {
            get().updateTask(id, response.data);
          } else {
            throw new Error(response.message || 'Failed to update task');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to update task';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      deleteTaskAPI: async (id: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await tasksAPI.deleteTask(id);
          
          if (response.success) {
            get().deleteTask(id);
          } else {
            throw new Error(response.message || 'Failed to delete task');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to delete task';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      // Task operations
      startTaskBlock: async (taskId: string, blockId: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await tasksAPI.startTaskBlock(taskId, blockId);
          
          if (response.success && response.data) {
            // Update the task with the started block
            get().updateTask(taskId, { 
              pomodoro_blocks: response.data.pomodoro_blocks 
            });
          } else {
            throw new Error(response.message || 'Failed to start task block');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to start task block';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      completeTaskBlock: async (taskId: string, blockId: string, proofData?: any) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await tasksAPI.completeTaskBlock(taskId, blockId, proofData);
          
          if (response.success && response.data) {
            // Update the task with completion data
            get().updateTask(taskId, { 
              pomodoro_blocks: response.data.pomodoro_blocks,
              currency_earned: response.data.currency_earned,
              actual_duration: response.data.actual_duration
            });
          } else {
            throw new Error(response.message || 'Failed to complete task block');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to complete task block';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      getTaskGuidance: async (taskId: string): Promise<string> => {
        try {
          const response = await tasksAPI.getTaskGuidance(taskId);
          
          if (response.success && response.data) {
            return response.data.guidance || 'No guidance available';
          } else {
            throw new Error(response.message || 'Failed to get task guidance');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to get task guidance';
          
          set({ error: errorMessage });
          return 'Unable to load guidance at this time';
        }
      },

      getMotivationalSupport: async (taskId: string): Promise<string> => {
        try {
          const response = await tasksAPI.getMotivationalSupport(taskId);
          
          if (response.success && response.data) {
            return response.data.motivation || 'You can do this!';
          } else {
            throw new Error(response.message || 'Failed to get motivational support');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to get motivational support';
          
          set({ error: errorMessage });
          return 'Stay focused and keep going!';
        }
      },

      // Pomodoro operations
      startPomodoro: (taskId: string, blockId: string) => {
        // This would typically start a timer and update UI state
        // For now, we'll just mark the block as in progress
        get().updateTask(taskId, {
          pomodoro_blocks: get().tasks
            .find(t => t.id === taskId)
            ?.pomodoro_blocks?.map(block => 
              block.id === blockId 
                ? { ...block, status: 'in_progress' as const }
                : block
            ) || []
        });
      },

      pausePomodoro: () => {
        // Implementation for pausing pomodoro timer
      },

      resumePomodoro: () => {
        // Implementation for resuming pomodoro timer
      },

      completePomodoro: async (proofData?: any) => {
        const { currentTask } = get();
        if (!currentTask) return;

        // Find the current in-progress block
        const currentBlock = currentTask.pomodoro_blocks?.find(
          block => block.status === 'in_progress'
        );

        if (currentBlock) {
          await get().completeTaskBlock(currentTask.id, currentBlock.id, proofData);
        }
      },

      // Filtering and search
      getFilteredTasks: () => {
        const { tasks, filters } = get();
        let filtered = tasks;

        if (filters.status) {
          filtered = filtered.filter(task => task.status === filters.status);
        }

        if (filters.priority) {
          filtered = filtered.filter(task => task.priority === filters.priority);
        }

        if (filters.category) {
          filtered = filtered.filter(task => task.category === filters.category);
        }

        if (filters.search) {
          const searchLower = filters.search.toLowerCase();
          filtered = filtered.filter(task =>
            task.title.toLowerCase().includes(searchLower) ||
            task.description?.toLowerCase().includes(searchLower) ||
            task.category.toLowerCase().includes(searchLower)
          );
        }

        return filtered;
      },

      getTasksByStatus: (status: string) => {
        return get().tasks.filter(task => task.status === status);
      },

      getTasksByCategory: (category: string) => {
        return get().tasks.filter(task => task.category === category);
      },

      searchTasks: (query: string) => {
        const searchLower = query.toLowerCase();
        return get().tasks.filter(task =>
          task.title.toLowerCase().includes(searchLower) ||
          task.description?.toLowerCase().includes(searchLower) ||
          task.category.toLowerCase().includes(searchLower)
        );
      },
    }),
    {
      name: 'focusforge-tasks',
      partialize: (state) => ({
        tasks: state.tasks,
        filters: state.filters,
      }),
    }
  )
);
