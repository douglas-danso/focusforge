import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { storeAPI } from '../services/api';
import { ApiError } from '../services/api';

export interface StoreItem {
  id: string;
  name: string;
  description: string;
  category: string;
  cost: number;
  duration: number; // in minutes
  image_url?: string;
  is_available: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: string;
  user_id: string;
  currency_balance: number;
  total_earned: number;
  total_spent: number;
  streak_count: number;
  level: number;
  experience_points: number;
  achievements: Achievement[];
  created_at: string;
  updated_at: string;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked_at: string;
  progress?: number;
  max_progress?: number;
}

export interface ActiveReward {
  id: string;
  user_id: string;
  item_name: string;
  item_category: string;
  duration_minutes: number;
  activated_at: string;
  expires_at: string;
  is_active: boolean;
}

export interface UserStats {
  total_tasks_completed: number;
  total_focus_time: number; // in minutes
  average_daily_productivity: number;
  best_productivity_day: string;
  current_streak: number;
  longest_streak: number;
  total_currency_earned: number;
  favorite_categories: string[];
}

export interface SpendingInsights {
  total_spent: number;
  spending_by_category: Record<string, number>;
  average_item_cost: number;
  most_expensive_purchase: string;
  spending_trend: 'increasing' | 'decreasing' | 'stable';
  recommendations: string[];
}

export interface LeaderboardEntry {
  user_id: string;
  username: string;
  avatar_url?: string;
  currency_balance: number;
  total_earned: number;
  streak_count: number;
  level: number;
  rank: number;
}

interface StoreState {
  items: StoreItem[];
  userProfile: UserProfile | null;
  activeRewards: ActiveReward[];
  userStats: UserStats | null;
  spendingInsights: SpendingInsights | null;
  leaderboard: LeaderboardEntry[];
  isLoading: boolean;
  error: string | null;
  filters: {
    category: string;
    minCost: number;
    maxCost: number;
    search: string;
  };
}

interface StoreActions {
  // Basic actions
  setItems: (items: StoreItem[]) => void;
  setUserProfile: (profile: UserProfile | null) => void;
  setActiveRewards: (rewards: ActiveReward[]) => void;
  setUserStats: (stats: UserStats | null) => void;
  setSpendingInsights: (insights: SpendingInsights | null) => void;
  setLeaderboard: (leaderboard: LeaderboardEntry[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  setFilters: (filters: Partial<StoreState['filters']>) => void;
  clearFilters: () => void;
  
  // Store operations
  addItem: (item: StoreItem) => void;
  updateItem: (id: string, updates: Partial<StoreItem>) => void;
  removeItem: (id: string) => void;
  
  // API methods
  fetchStoreItems: () => Promise<void>;
  fetchUserProfile: () => Promise<void>;
  fetchActiveRewards: () => Promise<void>;
  fetchUserStats: () => Promise<void>;
  fetchSpendingInsights: () => Promise<void>;
  fetchLeaderboard: () => Promise<void>;
  purchaseItem: (itemName: string) => Promise<void>;
  useReward: (rewardId: string) => Promise<void>;
  
  // Utility methods
  getFilteredItems: () => StoreItem[];
  getItemsByCategory: (category: string) => StoreItem[];
  getItemsByPriceRange: (min: number, max: number) => StoreItem[];
  searchItems: (query: string) => StoreItem[];
  getCurrencyBalance: () => number;
  getTotalEarned: () => number;
  getStreakCount: () => number;
  getLevel: () => number;
}

type StoreStore = StoreState & StoreActions;

export const useStoreStore = create<StoreStore>()(
  persist(
    (set, get) => ({
      // Initial state
      items: [],
      userProfile: null,
      activeRewards: [],
      userStats: null,
      spendingInsights: null,
      leaderboard: [],
      isLoading: false,
      error: null,
      filters: {
        category: '',
        minCost: 0,
        maxCost: 1000,
        search: '',
      },

      // Basic actions
      setItems: (items: StoreItem[]) => set({ items }),
      setUserProfile: (profile: UserProfile | null) => set({ userProfile: profile }),
      setActiveRewards: (rewards: ActiveReward[]) => set({ activeRewards: rewards }),
      setUserStats: (stats: UserStats | null) => set({ userStats: stats }),
      setSpendingInsights: (insights: SpendingInsights | null) => set({ spendingInsights: insights }),
      setLeaderboard: (leaderboard: LeaderboardEntry[]) => set({ leaderboard }),
      setLoading: (loading: boolean) => set({ isLoading: loading }),
      setError: (error: string | null) => set({ error }),
      clearError: () => set({ error: null }),
      
      setFilters: (filters: Partial<StoreState['filters']>) => 
        set((state) => ({ 
          filters: { ...state.filters, ...filters } 
        })),
      
      clearFilters: () => set({ 
        filters: { category: '', minCost: 0, maxCost: 1000, search: '' } 
      }),

      // Store operations
      addItem: (item: StoreItem) => set((state) => ({ 
        items: [...state.items, item] 
      })),
      
      updateItem: (id: string, updates: Partial<StoreItem>) => set((state) => ({
        items: state.items.map((item) =>
          item.id === id ? { ...item, ...updates } : item
        ),
      })),
      
      removeItem: (id: string) => set((state) => ({
        items: state.items.filter((item) => item.id !== id),
      })),

      // API methods
      fetchStoreItems: async () => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await storeAPI.getStoreItems();
          
          if (response.success && response.data) {
            set({ items: response.data });
          } else {
            throw new Error(response.message || 'Failed to fetch store items');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to fetch store items';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      fetchUserProfile: async () => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await storeAPI.getUserProfile();
          
          if (response.success && response.data) {
            set({ userProfile: response.data });
          } else {
            throw new Error(response.message || 'Failed to fetch user profile');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to fetch user profile';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      fetchActiveRewards: async () => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await storeAPI.getActiveRewards();
          
          if (response.success && response.data) {
            set({ activeRewards: response.data });
          } else {
            throw new Error(response.message || 'Failed to fetch active rewards');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to fetch active rewards';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      fetchUserStats: async () => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await storeAPI.getUserStats();
          
          if (response.success && response.data) {
            set({ userStats: response.data });
          } else {
            throw new Error(response.message || 'Failed to fetch user stats');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to fetch user stats';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      fetchSpendingInsights: async () => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await storeAPI.getSpendingInsights();
          
          if (response.success && response.data) {
            set({ spendingInsights: response.data });
          } else {
            throw new Error(response.message || 'Failed to fetch spending insights');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to fetch spending insights';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      fetchLeaderboard: async () => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await storeAPI.getLeaderboard();
          
          if (response.success && response.data) {
            set({ leaderboard: response.data });
          } else {
            throw new Error(response.message || 'Failed to fetch leaderboard');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to fetch leaderboard';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      purchaseItem: async (itemName: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await storeAPI.purchaseItem(itemName);
          
          if (response.success && response.data) {
            // Update user profile with new currency balance
            const { userProfile } = get();
            if (userProfile) {
              set({ 
                userProfile: { 
                  ...userProfile, 
                  currency_balance: response.data.new_balance || userProfile.currency_balance 
                } 
              });
            }
            
            // Refresh user profile to get updated data
            await get().fetchUserProfile();
          } else {
            throw new Error(response.message || 'Failed to purchase item');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to purchase item';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      useReward: async (rewardId: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await storeAPI.useReward(rewardId);
          
          if (response.success && response.data) {
            // Remove the used reward from active rewards
            set((state) => ({
              activeRewards: state.activeRewards.filter(reward => reward.id !== rewardId)
            }));
          } else {
            throw new Error(response.message || 'Failed to use reward');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to use reward';
          
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      // Utility methods
      getFilteredItems: () => {
        const { items, filters } = get();
        let filtered = items;

        if (filters.category) {
          filtered = filtered.filter(item => item.category === filters.category);
        }

        if (filters.minCost > 0) {
          filtered = filtered.filter(item => item.cost >= filters.minCost);
        }

        if (filters.maxCost < 1000) {
          filtered = filtered.filter(item => item.cost <= filters.maxCost);
        }

        if (filters.search) {
          const searchLower = filters.search.toLowerCase();
          filtered = filtered.filter(item =>
            item.name.toLowerCase().includes(searchLower) ||
            item.description.toLowerCase().includes(searchLower) ||
            item.category.toLowerCase().includes(searchLower)
          );
        }

        return filtered;
      },

      getItemsByCategory: (category: string) => {
        return get().items.filter(item => item.category === category);
      },

      getItemsByPriceRange: (min: number, max: number) => {
        return get().items.filter(item => item.cost >= min && item.cost <= max);
      },

      searchItems: (query: string) => {
        const searchLower = query.toLowerCase();
        return get().items.filter(item =>
          item.name.toLowerCase().includes(searchLower) ||
          item.description.toLowerCase().includes(searchLower) ||
          item.category.toLowerCase().includes(searchLower)
        );
      },

      getCurrencyBalance: () => {
        const { userProfile } = get();
        return userProfile?.currency_balance || 0;
      },

      getTotalEarned: () => {
        const { userProfile } = get();
        return userProfile?.total_earned || 0;
      },

      getStreakCount: () => {
        const { userProfile } = get();
        return userProfile?.streak_count || 0;
      },

      getLevel: () => {
        const { userProfile } = get();
        return userProfile?.level || 1;
      },
    }),
    {
      name: 'focusforge-store',
      partialize: (state) => ({
        items: state.items,
        userProfile: state.userProfile,
        activeRewards: state.activeRewards,
        userStats: state.userStats,
        spendingInsights: state.spendingInsights,
        leaderboard: state.leaderboard,
        filters: state.filters,
      }),
    }
  )
);

// Selectors
export const useStoreItems = () => useStoreStore((state) => state.items);
export const useUserProfile = () => useStoreStore((state) => state.userProfile);
export const useActiveRewards = () => useStoreStore((state) => state.activeRewards);
export const useLeaderboard = () => useStoreStore((state) => state.leaderboard);
export const useSelectedCategory = () => useStoreStore((state) => state.filters.category);
export const useStoreLoading = () => useStoreStore((state) => state.isLoading);
export const useStoreError = () => useStoreStore((state) => state.error);
export const useFilters = () => useStoreStore((state) => state.filters);
export const useUserStats = () => useStoreStore((state) => state.userStats);
export const useSpendingInsights = () => useStoreStore((state) => state.spendingInsights);

export const useStoreActions = () => useStoreStore((state) => ({
  fetchStoreItems: state.fetchStoreItems,
  fetchUserProfile: state.fetchUserProfile,
  fetchActiveRewards: state.fetchActiveRewards,
  fetchLeaderboard: state.fetchLeaderboard,
  purchaseItem: state.purchaseItem,
  useReward: state.useReward,
  setFilters: state.setFilters,
  clearFilters: state.clearFilters,
}));

export const useStoreComputed = () => useStoreStore((state) => ({
  getCurrencyBalance: state.getCurrencyBalance,
  getTotalEarned: state.getTotalEarned,
  getStreakCount: state.getStreakCount,
  getLevel: state.getLevel,
  getFilteredItems: state.getFilteredItems,
  getItemsByCategory: state.getItemsByCategory,
  getItemsByPriceRange: state.getItemsByPriceRange,
  searchItems: state.searchItems,
}));
