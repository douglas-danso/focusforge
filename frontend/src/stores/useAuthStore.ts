import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '../services/api';
import { ApiError } from '../services/api';

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  created_at: string;
  updated_at: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (token: string, user: User) => void;
  logout: () => void;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  // API methods
  googleAuthCallback: (code: string) => Promise<void>;
  getCurrentUser: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Basic actions
      login: (token: string, user: User) => {
        set({
          token,
          user,
          isAuthenticated: true,
          error: null,
        });
      },

      logout: () => {
        // Call logout API
        authAPI.logout().catch(console.error);
        
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },

      setUser: (user: User) => {
        set({ user });
      },

      setToken: (token: string) => {
        set({ token, isAuthenticated: true });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      setError: (error: string | null) => {
        set({ error });
      },

      clearError: () => {
        set({ error: null });
      },

      // API methods
      googleAuthCallback: async (code: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authAPI.googleCallback(code);
          
          if (response.success && response.data) {
            const { access_token, user } = response.data;
            get().login(access_token, user);
          } else {
            throw new Error(response.message || 'Authentication failed');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Authentication failed';
          
          set({ error: errorMessage });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      getCurrentUser: async () => {
        const { token } = get();
        if (!token) return;

        set({ isLoading: true, error: null });
        
        try {
          const response = await authAPI.getCurrentUser();
          
          if (response.success && response.data) {
            set({ user: response.data, isAuthenticated: true });
          } else {
            throw new Error(response.message || 'Failed to get user data');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Failed to get user data';
          
          set({ error: errorMessage });
          
          // If it's an auth error, logout
          if (error instanceof ApiError && error.status === 401) {
            get().logout();
          }
        } finally {
          set({ isLoading: false });
        }
      },

      refreshToken: async () => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authAPI.refreshToken();
          
          if (response.success && response.data) {
            const { access_token } = response.data;
            set({ token: access_token, isAuthenticated: true });
          } else {
            throw new Error(response.message || 'Token refresh failed');
          }
        } catch (error) {
          const errorMessage = error instanceof ApiError 
            ? error.message 
            : error instanceof Error 
              ? error.message 
              : 'Token refresh failed';
          
          set({ error: errorMessage });
          
          // If refresh fails, logout
          get().logout();
        } finally {
          set({ isLoading: false });
        }
      },
    }),
    {
      name: 'focusforge-auth',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Selectors for better performance
export const useAuth = () => useAuthStore((state) => ({
  user: state.user,
  token: state.token,
  isAuthenticated: state.isAuthenticated,
  isLoading: state.isLoading,
}));

export const useAuthActions = () => useAuthStore((state) => ({
  login: state.login,
  logout: state.logout,
  setUser: state.setUser,
  setLoading: state.setLoading,
  googleAuthCallback: state.googleAuthCallback,
  getCurrentUser: state.getCurrentUser,
  refreshToken: state.refreshToken,
}));
