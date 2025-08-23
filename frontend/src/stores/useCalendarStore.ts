import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  type: 'task' | 'pomodoro' | 'ritual' | 'external';
  color: string;
  description?: string;
  completed?: boolean;
  priority?: 'low' | 'medium' | 'high';
  source?: 'local' | 'google' | 'task';
  externalId?: string;
  recurrence?: {
    frequency: 'daily' | 'weekly' | 'monthly' | 'yearly';
    interval: number;
    endDate?: Date;
  };
}

export type SyncStatus = 'disconnected' | 'connecting' | 'connected' | 'syncing' | 'error';

interface CalendarStore {
  // State
  events: CalendarEvent[];
  syncStatus: SyncStatus;
  lastSync: Date | null;
  googleCalendarId: string | null;
  settings: {
    defaultView: 'month' | 'week' | 'day';
    workingHours: { start: number; end: number };
    showWeekends: boolean;
    timezone: string;
    autoSync: boolean;
    syncInterval: number; // minutes
  };

  // Actions
  addEvent: (event: Omit<CalendarEvent, 'id'>) => string;
  updateEvent: (id: string, updates: Partial<CalendarEvent>) => void;
  deleteEvent: (id: string) => void;
  getEventsForDate: (date: Date) => CalendarEvent[];
  getEventsForDateRange: (start: Date, end: Date) => CalendarEvent[];
  
  // Google Calendar Integration
  connectGoogleCalendar: () => Promise<void>;
  disconnectGoogleCalendar: () => void;
  syncGoogleCalendar: () => Promise<void>;
  setGoogleCalendarId: (id: string) => void;
  
  // Settings
  updateSettings: (settings: Partial<CalendarStore['settings']>) => void;
  
  // Utility
  clearAllEvents: () => void;
  exportEvents: () => string;
  importEvents: (data: string) => void;
}

export const useCalendarStore = create<CalendarStore>()(
  persist(
    (set, get) => ({
      // Initial state
      events: [],
      syncStatus: 'disconnected',
      lastSync: null,
      googleCalendarId: null,
      settings: {
        defaultView: 'month',
        workingHours: { start: 9, end: 17 },
        showWeekends: true,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        autoSync: true,
        syncInterval: 15,
      },

      // Actions
      addEvent: (eventData) => {
        const id = Date.now().toString();
        const newEvent: CalendarEvent = {
          ...eventData,
          id,
          start: new Date(eventData.start),
          end: new Date(eventData.end),
        };

        set((state) => ({
          events: [...state.events, newEvent],
        }));

        return id;
      },

      updateEvent: (id, updates) => {
        set((state) => ({
          events: state.events.map((event) =>
            event.id === id
              ? {
                  ...event,
                  ...updates,
                  start: updates.start ? new Date(updates.start) : event.start,
                  end: updates.end ? new Date(updates.end) : event.end,
                }
              : event
          ),
        }));
      },

      deleteEvent: (id) => {
        set((state) => ({
          events: state.events.filter((event) => event.id !== id),
        }));
      },

      getEventsForDate: (date) => {
        const state = get();
        const dateString = date.toDateString();
        
        return state.events.filter((event) => {
          const eventStart = new Date(event.start);
          const eventEnd = new Date(event.end);
          
          return (
            eventStart.toDateString() === dateString ||
            eventEnd.toDateString() === dateString ||
            (eventStart <= date && eventEnd >= date)
          );
        });
      },

      getEventsForDateRange: (start, end) => {
        const state = get();
        
        return state.events.filter((event) => {
          const eventStart = new Date(event.start);
          const eventEnd = new Date(event.end);
          
          return (
            (eventStart >= start && eventStart <= end) ||
            (eventEnd >= start && eventEnd <= end) ||
            (eventStart <= start && eventEnd >= end)
          );
        });
      },

      // Google Calendar Integration
      connectGoogleCalendar: async () => {
        set({ syncStatus: 'connecting' });
        
        try {
          // Simulate Google Calendar connection
          // In a real implementation, this would handle OAuth flow
          await new Promise((resolve) => setTimeout(resolve, 2000));
          
          set({
            syncStatus: 'connected',
            lastSync: new Date(),
            googleCalendarId: 'primary',
          });
        } catch (error) {
          set({ syncStatus: 'error' });
          throw error;
        }
      },

      disconnectGoogleCalendar: () => {
        set({
          syncStatus: 'disconnected',
          lastSync: null,
          googleCalendarId: null,
        });
      },

      syncGoogleCalendar: async () => {
        const state = get();
        if (state.syncStatus !== 'connected') {
          throw new Error('Google Calendar not connected');
        }

        set({ syncStatus: 'syncing' });
        
        try {
          // Simulate Google Calendar sync
          // In a real implementation, this would fetch events from Google Calendar API
          await new Promise((resolve) => setTimeout(resolve, 3000));
          
          // Mock external events from Google Calendar
          const mockExternalEvents: CalendarEvent[] = [
            {
              id: `google-${Date.now()}-1`,
              title: 'Team Meeting',
              start: new Date(Date.now() + 24 * 60 * 60 * 1000), // Tomorrow
              end: new Date(Date.now() + 24 * 60 * 60 * 1000 + 60 * 60 * 1000), // +1 hour
              type: 'external',
              color: 'bg-blue-100 text-blue-800',
              source: 'google',
              externalId: 'google-event-1',
            },
            {
              id: `google-${Date.now()}-2`,
              title: 'Client Call',
              start: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000), // Day after tomorrow
              end: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000 + 30 * 60 * 1000), // +30 min
              type: 'external',
              color: 'bg-green-100 text-green-800',
              source: 'google',
              externalId: 'google-event-2',
            },
          ];

          set((state) => ({
            events: [
              ...state.events.filter((event) => event.source !== 'google'),
              ...mockExternalEvents,
            ],
            syncStatus: 'connected',
            lastSync: new Date(),
          }));
        } catch (error) {
          set({ syncStatus: 'error' });
          throw error;
        }
      },

      setGoogleCalendarId: (id) => {
        set({ googleCalendarId: id });
      },

      // Settings
      updateSettings: (newSettings) => {
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
        }));
      },

      // Utility
      clearAllEvents: () => {
        set({ events: [] });
      },

      exportEvents: () => {
        const state = get();
        return JSON.stringify(state.events, null, 2);
      },

      importEvents: (data) => {
        try {
          const events = JSON.parse(data);
          if (Array.isArray(events)) {
            set({ events });
          }
        } catch (error) {
          console.error('Failed to import events:', error);
        }
      },
    }),
    {
      name: 'focusforge-calendar',
      partialize: (state) => ({
        events: state.events,
        settings: state.settings,
        googleCalendarId: state.googleCalendarId,
        lastSync: state.lastSync,
      }),
    }
  )
);
