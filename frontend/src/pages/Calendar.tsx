import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Calendar as CalendarIcon, 
  ChevronLeft, 
  ChevronRight, 
  Plus,
  Clock,
  CheckCircle,
  AlertCircle,
  Settings,
  RefreshCw,
  ExternalLink,
  Filter,
  Grid3X3,
  List,
  BarChart3
} from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useCalendarStore } from '../stores/useCalendarStore';
import { useTaskStore } from '../stores/useTaskStore';
import { useUIStore } from '../stores/useUIStore';

type CalendarView = 'month' | 'week' | 'day';
type CalendarEvent = {
  id: string;
  title: string;
  start: Date;
  end: Date;
  type: 'task' | 'pomodoro' | 'ritual' | 'external';
  color: string;
  description?: string;
  completed?: boolean;
  priority?: 'low' | 'medium' | 'high';
};

const Calendar: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<CalendarView>('month');
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [showEventModal, setShowEventModal] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [filters, setFilters] = useState({
    tasks: true,
    pomodoro: true,
    rituals: true,
    external: true
  });

  const { events, syncStatus, syncGoogleCalendar, addEvent, updateEvent, deleteEvent } = useCalendarStore();
  const { tasks } = useTaskStore();
  const { addNotification } = useUIStore();

  // Calendar navigation
  const goToPrevious = () => {
    const newDate = new Date(currentDate);
    if (view === 'month') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else if (view === 'week') {
      newDate.setDate(newDate.getDate() - 7);
    } else {
      newDate.setDate(newDate.getDate() - 1);
    }
    setCurrentDate(newDate);
  };

  const goToNext = () => {
    const newDate = new Date(currentDate);
    if (view === 'month') {
      newDate.setMonth(newDate.getMonth() + 1);
    } else if (view === 'week') {
      newDate.setDate(newDate.getDate() + 7);
    } else {
      newDate.setDate(newDate.getDate() + 1);
    }
    setCurrentDate(newDate);
  };

  const goToToday = () => {
    setCurrentDate(new Date());
    setSelectedDate(new Date());
  };

  // Calendar data generation
  const calendarData = useMemo(() => {
    if (view === 'month') {
      return generateMonthView(currentDate);
    } else if (view === 'week') {
      return generateWeekView(currentDate);
    } else {
      return generateDayView(currentDate);
    }
  }, [currentDate, view, events, tasks]) as any;

  // Generate month view data
  const generateMonthView = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const weeks: Array<Array<{
      date: Date;
      isCurrentMonth: boolean;
      isToday: boolean;
      events: CalendarEvent[];
    }>> = [];
    let currentWeek: Array<{
      date: Date;
      isCurrentMonth: boolean;
      isToday: boolean;
      events: CalendarEvent[];
    }> = [];
    let currentDate = new Date(startDate);
    
    while (currentDate <= lastDay || currentWeek.length < 7) {
      currentWeek.push({
        date: new Date(currentDate),
        isCurrentMonth: currentDate.getMonth() === month,
        isToday: currentDate.toDateString() === new Date().toDateString(),
        events: getEventsForDate(currentDate)
      });
      
      if (currentWeek.length === 7) {
        weeks.push(currentWeek);
        currentWeek = [];
      }
      
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    if (currentWeek.length > 0) {
      weeks.push(currentWeek);
    }
    
    return weeks;
  };

  // Generate week view data
  const generateWeekView = (date: Date) => {
    const startOfWeek = new Date(date);
    startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay());
    
    const days: Array<{
      date: Date;
      isToday: boolean;
      events: CalendarEvent[];
    }> = [];
    for (let i = 0; i < 7; i++) {
      const dayDate = new Date(startOfWeek);
      dayDate.setDate(startOfWeek.getDate() + i);
      days.push({
        date: dayDate,
        isToday: dayDate.toDateString() === new Date().toDateString(),
        events: getEventsForDate(dayDate)
      });
    }
    
    return days;
  };

  // Generate day view data
  const generateDayView = (date: Date) => {
    const hours: Array<{
      hour: number;
      time: string;
      events: CalendarEvent[];
    }> = [];
    for (let hour = 0; hour < 24; hour++) {
      const hourDate = new Date(date);
      hourDate.setHours(hour, 0, 0, 0);
      hours.push({
        hour,
        time: `${hour.toString().padStart(2, '0')}:00`,
        events: getEventsForHour(date, hour)
      });
    }
    
    return hours;
  };

  // Get events for a specific date
  const getEventsForDate = (date: Date): CalendarEvent[] => {
    const dateString = date.toDateString();
    return events.filter(event => 
      event.start.toDateString() === dateString ||
      event.end.toDateString() === dateString ||
      (event.start <= date && event.end >= date)
    );
  };

  // Get events for a specific hour
  const getEventsForHour = (date: Date, hour: number): CalendarEvent[] => {
    const hourStart = new Date(date);
    hourStart.setHours(hour, 0, 0, 0);
    const hourEnd = new Date(date);
    hourEnd.setHours(hour + 1, 0, 0, 0);
    
    return events.filter(event => 
      event.start < hourEnd && event.end > hourStart
    );
  };

  // Handle Google Calendar sync
  const handleGoogleSync = async () => {
    try {
      await syncGoogleCalendar();
      addNotification({
        type: 'success',
        title: 'Google Calendar',
        message: 'Google Calendar synced successfully!'
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Google Calendar',
        message: 'Failed to sync Google Calendar'
      });
    }
  };

  // Render month view
  const renderMonthView = () => {
    const monthData = calendarData as Array<Array<{
      date: Date;
      isCurrentMonth: boolean;
      isToday: boolean;
      events: CalendarEvent[];
    }>>;
    
    return (
      <div className="grid grid-cols-7 gap-1">
        {/* Day headers */}
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className="p-2 text-center text-sm font-medium text-gray-500 bg-gray-50 rounded-lg">
            {day}
          </div>
        ))}
        
        {/* Calendar days */}
        {monthData.map((week, weekIndex) => (
          <React.Fragment key={weekIndex}>
            {week.map((day, dayIndex) => (
              <motion.div
                key={dayIndex}
                whileHover={{ scale: 1.02 }}
                className={`min-h-[120px] p-2 border border-gray-200 rounded-lg cursor-pointer transition-all ${
                  day.isToday ? 'bg-blue-50 border-blue-300' : ''
                } ${!day.isCurrentMonth ? 'bg-gray-50 text-gray-400' : 'bg-white'}`}
                onClick={() => setSelectedDate(day.date)}
              >
                <div className="text-sm font-medium mb-2">
                  {day.date.getDate()}
                </div>
                
                {/* Events for this day */}
                <div className="space-y-1">
                  {day.events.slice(0, 3).map((event: CalendarEvent) => (
                    <div
                      key={event.id}
                      className={`text-xs p-1 rounded truncate ${event.color}`}
                      title={event.title}
                    >
                      {event.title}
                    </div>
                  ))}
                  {day.events.length > 3 && (
                    <div className="text-xs text-gray-500 text-center">
                      +{day.events.length - 3} more
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </React.Fragment>
        ))}
      </div>
    );
  };

  // Render week view
  const renderWeekView = () => {
    const weekData = calendarData as Array<{
      date: Date;
      isToday: boolean;
      events: CalendarEvent[];
    }>;
    
    return (
      <div className="grid grid-cols-7 gap-4">
        {weekData.map((day, index) => (
          <div key={index} className="min-h-[400px]">
            <div className={`text-center p-2 mb-2 rounded-lg ${
              day.isToday ? 'bg-blue-100 text-blue-800' : 'bg-gray-100'
            }`}>
              <div className="text-sm font-medium">
                {day.date.toLocaleDateString('en-US', { weekday: 'short' })}
              </div>
              <div className="text-lg font-bold">
                {day.date.getDate()}
              </div>
            </div>
            
            <div className="space-y-2">
              {day.events.map((event: CalendarEvent) => (
                <motion.div
                  key={event.id}
                  whileHover={{ scale: 1.02 }}
                  className={`p-2 rounded-lg text-sm ${event.color} cursor-pointer`}
                  title={event.title}
                >
                  <div className="font-medium truncate">{event.title}</div>
                  <div className="text-xs opacity-75">
                    {event.start.toLocaleTimeString('en-US', { 
                      hour: 'numeric', 
                      minute: '2-digit' 
                    })}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Render day view
  const renderDayView = () => {
    const dayData = calendarData as Array<{
      hour: number;
      time: string;
      events: CalendarEvent[];
    }>;
    
    return (
      <div className="space-y-2">
        {dayData.map((hour, index) => (
          <div key={index} className="flex">
            <div className="w-20 text-sm text-gray-500 p-2 border-r border-gray-200">
              {hour.time}
            </div>
            <div className="flex-1 p-2 border-b border-gray-100 min-h-[60px]">
              {hour.events.map((event: CalendarEvent) => (
                <motion.div
                  key={event.id}
                  whileHover={{ scale: 1.02 }}
                  className={`p-2 rounded-lg text-sm ${event.color} cursor-pointer mb-2`}
                  title={event.title}
                >
                  <div className="font-medium">{event.title}</div>
                  <div className="text-xs opacity-75">
                    {event.start.toLocaleTimeString('en-US', { 
                      hour: 'numeric', 
                      minute: '2-digit' 
                    })} - {event.end.toLocaleTimeString('en-US', { 
                      hour: 'numeric', 
                      minute: '2-digit' 
                    })}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Productivity insights
  const productivityInsights = useMemo(() => {
    const today = new Date();
    const todayEvents = getEventsForDate(today);
    const completedTasks = todayEvents.filter(event => 
      event.type === 'task' && event.completed
    ).length;
    const totalTasks = todayEvents.filter(event => 
      event.type === 'task'
    ).length;
    const focusTime = todayEvents.filter(event => 
      event.type === 'pomodoro'
    ).reduce((total, event) => {
      const duration = (event.end.getTime() - event.start.getTime()) / (1000 * 60);
      return total + duration;
    }, 0);

    return {
      completionRate: totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0,
      focusTime,
      totalEvents: todayEvents.length,
      productivity: totalTasks > 0 ? Math.min(100, (completedTasks / totalTasks) * 100 + focusTime / 2) : 0
    };
  }, [events, currentDate]);

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Calendar</h1>
              <p className="text-gray-600">Manage your schedule and track productivity</p>
            </div>
            
            <div className="flex items-center space-x-3">
              <Button
                onClick={handleGoogleSync}
                variant="outline"
                className="flex items-center space-x-2"
              >
                <RefreshCw className={`w-4 h-4 ${syncStatus === 'syncing' ? 'animate-spin' : ''}`} />
                <span>Sync Google</span>
              </Button>
              
              <Button
                onClick={() => setShowSettings(true)}
                variant="outline"
                size="sm"
              >
                <Settings className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Sync Status */}
          <div className="flex items-center space-x-4 text-sm">
            <div className={`flex items-center space-x-2 ${
              syncStatus === 'connected' ? 'text-green-600' : 
              syncStatus === 'disconnected' ? 'text-red-600' : 'text-yellow-600'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                syncStatus === 'connected' ? 'bg-green-500' : 
                syncStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500'
              }`} />
              <span>
                Google Calendar: {syncStatus === 'connected' ? 'Connected' : 
                syncStatus === 'disconnected' ? 'Disconnected' : 'Syncing...'}
              </span>
            </div>
            
            {syncStatus === 'connected' && (
              <Button
                onClick={handleGoogleSync}
                variant="ghost"
                size="sm"
                className="text-blue-600 hover:text-blue-700"
              >
                <ExternalLink className="w-4 h-4 mr-1" />
                Open Google Calendar
              </Button>
            )}
          </div>
        </motion.div>

        {/* Productivity Insights */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
        >
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{productivityInsights.completionRate.toFixed(0)}%</div>
            <div className="text-sm text-gray-600">Task Completion</div>
          </Card>
          
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{productivityInsights.focusTime.toFixed(0)}m</div>
            <div className="text-sm text-gray-600">Focus Time</div>
          </Card>
          
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">{productivityInsights.totalEvents}</div>
            <div className="text-sm text-gray-600">Today's Events</div>
          </Card>
          
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-orange-600">{productivityInsights.productivity.toFixed(0)}%</div>
            <div className="text-sm text-gray-600">Productivity Score</div>
          </Card>
        </motion.div>

        {/* Calendar Controls */}
        <Card className="p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button onClick={goToPrevious} variant="outline" size="sm">
                <ChevronLeft className="w-4 h-4" />
              </Button>
              
              <Button onClick={goToToday} variant="outline" size="sm">
                Today
              </Button>
              
              <Button onClick={goToNext} variant="outline" size="sm">
                <ChevronRight className="w-4 h-4" />
              </Button>
              
              <h2 className="text-xl font-semibold">
                {currentDate.toLocaleDateString('en-US', { 
                  month: 'long', 
                  year: 'numeric' 
                })}
              </h2>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                onClick={() => setView('month')}
                variant={view === 'month' ? 'default' : 'outline'}
                size="sm"
              >
                Month
              </Button>
              <Button
                onClick={() => setView('week')}
                variant={view === 'week' ? 'default' : 'outline'}
                size="sm"
              >
                Week
              </Button>
              <Button
                onClick={() => setView('day')}
                variant={view === 'day' ? 'default' : 'outline'}
                size="sm"
              >
                Day
              </Button>
            </div>
          </div>
        </Card>

        {/* Filters */}
        <Card className="p-4 mb-6">
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">Show:</span>
            {Object.entries(filters).map(([key, value]) => (
              <label key={key} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={value}
                  onChange={(e) => setFilters(prev => ({ ...prev, [key]: e.target.checked }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 capitalize">{key}</span>
              </label>
            ))}
          </div>
        </Card>

        {/* Calendar View */}
        <Card className="p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={view}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              {view === 'month' && renderMonthView()}
              {view === 'week' && renderWeekView()}
              {view === 'day' && renderDayView()}
            </motion.div>
          </AnimatePresence>
        </Card>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-8 text-center"
        >
          <Button
            onClick={() => setShowEventModal(true)}
            size="lg"
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add Event
          </Button>
        </motion.div>
      </div>
    </div>
  );
};

export default Calendar;
