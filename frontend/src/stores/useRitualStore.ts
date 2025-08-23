import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface RitualStep {
  id: string;
  type: 'environment' | 'breathing' | 'meditation' | 'spotify' | 'intention' | 'custom';
  title: string;
  description: string;
  duration: number;
  config: any;
}

export interface RitualTemplate {
  id: string;
  name: string;
  description: string;
  steps: RitualStep[];
  category: string;
  estimatedDuration: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  createdAt: Date;
  usageCount: number;
  averageRating: number;
}

export interface RitualExecution {
  id: string;
  ritualId: string;
  ritualName: string;
  startedAt: Date;
  completedAt?: Date;
  duration: number;
  rating?: number;
  notes?: string;
  steps: {
    stepId: string;
    stepTitle: string;
    completed: boolean;
    timeSpent: number;
  }[];
}

interface RitualStore {
  // State
  rituals: RitualTemplate[];
  executions: RitualExecution[];
  currentExecution: RitualExecution | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  createRitual: (ritual: Omit<RitualTemplate, 'id' | 'createdAt' | 'usageCount' | 'averageRating'>) => void;
  updateRitual: (id: string, updates: Partial<RitualTemplate>) => void;
  deleteRitual: (id: string) => void;
  startRitual: (ritual: RitualTemplate) => void;
  completeRitual: (executionId: string, rating?: number, notes?: string) => void;
  pauseRitual: () => void;
  resumeRitual: () => void;
  getRitualStats: (ritualId: string) => {
    totalExecutions: number;
    averageRating: number;
    totalTimeSpent: number;
    successRate: number;
  };
  getCategoryStats: () => Record<string, { count: number; totalTime: number }>;
  clearError: () => void;
}

export const useRitualStore = create<RitualStore>()(
  persist(
    (set, get) => ({
      // Initial state
      rituals: [],
      executions: [],
      currentExecution: null,
      isLoading: false,
      error: null,

      // Actions
      createRitual: (ritualData) => {
        const newRitual: RitualTemplate = {
          ...ritualData,
          id: Date.now().toString(),
          createdAt: new Date(),
          usageCount: 0,
          averageRating: 0,
        };

        set((state) => ({
          rituals: [...state.rituals, newRitual],
        }));
      },

      updateRitual: (id, updates) => {
        set((state) => ({
          rituals: state.rituals.map((ritual) =>
            ritual.id === id ? { ...ritual, ...updates } : ritual
          ),
        }));
      },

      deleteRitual: (id) => {
        set((state) => ({
          rituals: state.rituals.filter((ritual) => ritual.id !== id),
          executions: state.executions.filter((execution) => execution.ritualId !== id),
        }));
      },

      startRitual: (ritual) => {
        const execution: RitualExecution = {
          id: Date.now().toString(),
          ritualId: ritual.id,
          ritualName: ritual.name,
          startedAt: new Date(),
          duration: 0,
          steps: ritual.steps.map((step) => ({
            stepId: step.id,
            stepTitle: step.title,
            completed: false,
            timeSpent: 0,
          })),
        };

        // Update usage count
        const updatedRituals = get().rituals.map((r) =>
          r.id === ritual.id ? { ...r, usageCount: r.usageCount + 1 } : r
        );

        set((state) => ({
          currentExecution: execution,
          executions: [...state.executions, execution],
          rituals: updatedRituals,
        }));
      },

      completeRitual: (executionId, rating, notes) => {
        const now = new Date();
        
        set((state) => ({
          executions: state.executions.map((execution) => {
            if (execution.id === executionId) {
              const duration = now.getTime() - execution.startedAt.getTime();
              return {
                ...execution,
                completedAt: now,
                duration: Math.round(duration / 1000 / 60), // Convert to minutes
                rating,
                notes,
                steps: execution.steps.map((step) => ({ ...step, completed: true })),
              };
            }
            return execution;
          }),
          currentExecution: null,
        }));

        // Update ritual average rating if rating provided
        if (rating) {
          const execution = get().executions.find((e) => e.id === executionId);
          if (execution) {
            const ritual = get().rituals.find((r) => r.id === execution.ritualId);
            if (ritual) {
              const completedExecutions = get().executions.filter(
                (e) => e.ritualId === execution.ritualId && e.rating
              );
              const newAverageRating =
                completedExecutions.reduce((sum, e) => sum + (e.rating || 0), 0) /
                completedExecutions.length;

              get().updateRitual(ritual.id, { averageRating: newAverageRating });
            }
          }
        }
      },

      pauseRitual: () => {
        // Implementation for pausing ritual execution
        // This could be used for meditation timers or step-by-step execution
      },

      resumeRitual: () => {
        // Implementation for resuming paused ritual execution
      },

      getRitualStats: (ritualId) => {
        const state = get();
        const ritualExecutions = state.executions.filter(
          (execution) => execution.ritualId === ritualId && execution.completedAt
        );

        const totalExecutions = ritualExecutions.length;
        const totalTimeSpent = ritualExecutions.reduce((sum, e) => sum + e.duration, 0);
        const averageRating =
          ritualExecutions.reduce((sum, e) => sum + (e.rating || 0), 0) / totalExecutions || 0;
        const successRate = totalExecutions > 0 ? 100 : 0; // Could be enhanced with more logic

        return {
          totalExecutions,
          averageRating,
          totalTimeSpent,
          successRate,
        };
      },

      getCategoryStats: () => {
        const state = get();
        const stats: Record<string, { count: number; totalTime: number }> = {};

        state.rituals.forEach((ritual) => {
          if (!stats[ritual.category]) {
            stats[ritual.category] = { count: 0, totalTime: 0 };
          }
          stats[ritual.category].count += 1;
          stats[ritual.category].totalTime += ritual.estimatedDuration;
        });

        return stats;
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'focusforge-rituals',
      partialize: (state) => ({
        rituals: state.rituals,
        executions: state.executions,
      }),
    }
  )
);
