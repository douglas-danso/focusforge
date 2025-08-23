import { create } from 'zustand';
import { persist } from 'zustand/middleware';

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
  timestamp: number;
}

export interface UIState {
  theme: 'light' | 'dark' | 'system';
  sidebarOpen: boolean;
  mobileMenuOpen: boolean;
  notifications: Notification[];
  modals: {
    taskCreate: boolean;
    taskDetail: boolean;
    moodLog: boolean;
    ritualBuilder: boolean;
    calendarSync: boolean;
  };
  loadingStates: {
    global: boolean;
    auth: boolean;
    tasks: boolean;
    mood: boolean;
    store: boolean;
    calendar: boolean;
  };
  errors: Record<string, string | null>;
  lastError: string | null;
}

interface UIActions {
  // Theme
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  toggleTheme: () => void;
  
  // Navigation
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setMobileMenuOpen: (open: boolean) => void;
  toggleMobileMenu: () => void;
  
  // Notifications
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  clearNotificationsByType: (type: Notification['type']) => void;
  
  // Modals
  openModal: (modalName: keyof UIState['modals']) => void;
  closeModal: (modalName: keyof UIState['modals']) => void;
  closeAllModals: () => void;
  
  // Loading states
  setLoading: (key: keyof UIState['loadingStates'], loading: boolean) => void;
  setGlobalLoading: (loading: boolean) => void;
  
  // Error handling
  setError: (key: string, error: string | null) => void;
  clearError: (key: string) => void;
  clearAllErrors: () => void;
  setLastError: (error: string | null) => void;
  
  // Utility
  resetUI: () => void;
}

type UIStore = UIState & UIActions;

const initialState: UIState = {
  theme: 'system',
  sidebarOpen: true,
  mobileMenuOpen: false,
  notifications: [],
  modals: {
    taskCreate: false,
    taskDetail: false,
    moodLog: false,
    ritualBuilder: false,
    calendarSync: false,
  },
  loadingStates: {
    global: false,
    auth: false,
    tasks: false,
    mood: false,
    store: false,
    calendar: false,
  },
  errors: {},
  lastError: null,
};

export const useUIStore = create<UIStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      // Theme
      setTheme: (theme: 'light' | 'dark' | 'system') => {
        set({ theme });
        
        // Apply theme to document
        if (theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      },

      toggleTheme: () => {
        const { theme } = get();
        const newTheme = theme === 'light' ? 'dark' : 'light';
        get().setTheme(newTheme);
      },

      // Navigation
      setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setMobileMenuOpen: (open: boolean) => set({ mobileMenuOpen: open }),
      toggleMobileMenu: () => set((state) => ({ mobileMenuOpen: !state.mobileMenuOpen })),

      // Notifications
      addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => {
        const id = Math.random().toString(36).substr(2, 9);
        const timestamp = Date.now();
        const newNotification: Notification = {
          ...notification,
          id,
          timestamp,
        };

        set((state) => ({
          notifications: [...state.notifications, newNotification],
        }));

        // Auto-remove notification after duration (default: 5000ms)
        const duration = notification.duration || 5000;
        if (duration > 0) {
          setTimeout(() => {
            get().removeNotification(id);
          }, duration);
        }
      },

      removeNotification: (id: string) => {
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        }));
      },

      clearNotifications: () => set({ notifications: [] }),

      clearNotificationsByType: (type: Notification['type']) => {
        set((state) => ({
          notifications: state.notifications.filter((n) => n.type !== type),
        }));
      },

      // Modals
      openModal: (modalName: keyof UIState['modals']) => {
        set((state) => ({
          modals: { ...state.modals, [modalName]: true },
        }));
      },

      closeModal: (modalName: keyof UIState['modals']) => {
        set((state) => ({
          modals: { ...state.modals, [modalName]: false },
        }));
      },

      closeAllModals: () => {
        set((state) => ({
          modals: Object.keys(state.modals).reduce(
            (acc, key) => ({ ...acc, [key]: false }),
            {} as UIState['modals']
          ),
        }));
      },

      // Loading states
      setLoading: (key: keyof UIState['loadingStates'], loading: boolean) => {
        set((state) => ({
          loadingStates: { ...state.loadingStates, [key]: loading },
        }));
      },

      setGlobalLoading: (loading: boolean) => {
        set((state) => ({
          loadingStates: { ...state.loadingStates, global: loading },
        }));
      },

      // Error handling
      setError: (key: string, error: string | null) => {
        set((state) => ({
          errors: { ...state.errors, [key]: error },
          lastError: error,
        }));
      },

      clearError: (key: string) => {
        set((state) => ({
          errors: { ...state.errors, [key]: null },
        }));
      },

      clearAllErrors: () => {
        set({ errors: {}, lastError: null });
      },

      setLastError: (error: string | null) => {
        set({ lastError: error });
      },

      // Utility
      resetUI: () => {
        set({
          ...initialState,
          theme: get().theme, // Preserve theme preference
        });
      },
    }),
    {
      name: 'focusforge-ui',
      partialize: (state) => ({
        theme: state.theme,
        sidebarOpen: state.sidebarOpen,
        modals: state.modals,
      }),
    }
  )
);

// Selectors
export const useTheme = () => useUIStore((state) => state.theme);
export const useSidebarOpen = () => useUIStore((state) => state.sidebarOpen);
export const useMobileMenuOpen = () => useUIStore((state) => state.mobileMenuOpen);
export const useNotifications = () => useUIStore((state) => state.notifications);
export const useModals = () => useUIStore((state) => state.modals);
export const useLoadingStates = () => useUIStore((state) => state.loadingStates);
export const useErrors = () => useUIStore((state) => state.errors);
export const useLastError = () => useUIStore((state) => state.lastError);

export const useUIActions = () => useUIStore((state) => ({
  setTheme: state.setTheme,
  toggleTheme: state.toggleTheme,
  setSidebarOpen: state.setSidebarOpen,
  toggleSidebar: state.toggleSidebar,
  setMobileMenuOpen: state.setMobileMenuOpen,
  toggleMobileMenu: state.toggleMobileMenu,
  addNotification: state.addNotification,
  removeNotification: state.removeNotification,
  clearNotifications: state.clearNotifications,
  clearNotificationsByType: state.clearNotificationsByType,
  openModal: state.openModal,
  closeModal: state.closeModal,
  closeAllModals: state.closeAllModals,
  setLoading: state.setLoading,
  setGlobalLoading: state.setGlobalLoading,
  setError: state.setError,
  clearError: state.clearError,
  clearAllErrors: state.clearAllErrors,
  setLastError: state.setLastError,
  resetUI: state.resetUI,
}));
