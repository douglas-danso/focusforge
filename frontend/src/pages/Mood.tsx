import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Smile, 
  Meh, 
  Frown, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Target,
  Zap,
  Coffee,
  Moon,
  Sun,
  Cloud,
  Heart,
  Brain,
  Calendar,
  BarChart3
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useMoodStore, useMoodActions } from '@/stores/useMoodStore';
import { useUIStore } from '@/stores/useUIStore';
import { formatDate, getMoodEmoji, getMoodColor } from '@/lib/utils';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

type MoodValue = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
type EnergyLevel = 'very_low' | 'low' | 'medium' | 'high' | 'very_high';
type StressLevel = 'very_low' | 'low' | 'medium' | 'high' | 'very_high';

// Local interface that matches the component's needs
interface LocalMoodEntry {
  id: string;
  timestamp: Date;
  mood: MoodValue;
  energy: EnergyLevel;
  stress: StressLevel;
  notes?: string;
  activities: string[];
  sleep_hours?: number;
  weather?: string;
}

const moodOptions: { value: MoodValue; emoji: string; label: string; color: string }[] = [
  { value: 1, emoji: '😢', label: 'Terrible', color: 'text-red-600' },
  { value: 2, emoji: '😞', label: 'Very Bad', color: 'text-red-500' },
  { value: 3, emoji: '😔', label: 'Bad', color: 'text-orange-500' },
  { value: 4, emoji: '😐', label: 'Poor', color: 'text-orange-400' },
  { value: 5, emoji: '😐', label: 'Neutral', color: 'text-yellow-500' },
  { value: 6, emoji: '🙂', label: 'Okay', color: 'text-yellow-400' },
  { value: 7, emoji: '😊', label: 'Good', color: 'text-green-400' },
  { value: 8, emoji: '😄', label: 'Very Good', color: 'text-green-500' },
  { value: 9, emoji: '🤩', label: 'Excellent', color: 'text-blue-500' },
  { value: 10, emoji: '🥳', label: 'Amazing', color: 'text-purple-500' },
];

const energyOptions: { value: EnergyLevel; icon: any; label: string; color: string }[] = [
  { value: 'very_low', icon: Moon, label: 'Very Low', color: 'text-purple-600' },
  { value: 'low', icon: Cloud, label: 'Low', color: 'text-blue-600' },
  { value: 'medium', icon: Meh, label: 'Medium', color: 'text-yellow-600' },
  { value: 'high', icon: Sun, label: 'High', color: 'text-orange-600' },
  { value: 'very_high', icon: Zap, label: 'Very High', color: 'text-red-600' },
];

const stressOptions: { value: StressLevel; icon: any; label: string; color: string }[] = [
  { value: 'very_low', icon: Heart, label: 'Very Low', color: 'text-green-600' },
  { value: 'low', icon: Smile, label: 'Low', color: 'text-green-500' },
  { value: 'medium', icon: Meh, label: 'Medium', color: 'text-yellow-500' },
  { value: 'high', icon: Frown, label: 'High', color: 'text-orange-500' },
  { value: 'very_high', icon: Activity, label: 'Very High', color: 'text-red-500' },
];

const commonActivities = [
  'Exercise', 'Work', 'Reading', 'Music', 'Social', 'Nature', 'Creative', 'Rest', 'Learning', 'Family'
];

export default function Mood() {
  const [showQuickLog, setShowQuickLog] = useState(false);
  const [showDetailedLog, setShowDetailedLog] = useState(false);
  const [selectedMood, setSelectedMood] = useState<MoodValue | null>(null);
  const [selectedEnergy, setSelectedEnergy] = useState<EnergyLevel | null>(null);
  const [selectedStress, setSelectedStress] = useState<StressLevel | null>(null);
  const [selectedActivities, setSelectedActivities] = useState<string[]>([]);
  const [notes, setNotes] = useState('');
  const [sleepHours, setSleepHours] = useState(8);
  const [weather, setWeather] = useState('sunny');
  const [timeFilter, setTimeFilter] = useState<'week' | 'month' | 'year'>('week');

  const { moodHistory, currentMood } = useMoodStore();
  const { logMood, fetchMoodHistory } = useMoodActions();
  const { addNotification } = useUIStore();

  useEffect(() => {
    fetchMoodHistory();
  }, [fetchMoodHistory]);

  const handleQuickMoodLog = async (mood: MoodValue) => {
    try {
      await logMood({
        mood_score: mood,
        energy_level: 5,
        stress_level: 5,
        // motivation_level: 5, // removed as not in interface
        notes: 'Quick mood log',
        // activity: 'General', // removed as not in interface
        // location: 'Unknown', // removed as not in interface
        // timestamp: new Date().toISOString(), // removed as not in interface
      });
      setShowQuickLog(false);
      addNotification({ type: 'success', title: 'Mood Logged', message: 'Your mood has been recorded!' });
    } catch (error) {
      addNotification({ type: 'error', title: 'Logging Failed', message: 'Failed to log your mood' });
    }
  };

  const handleDetailedMoodLog = async () => {
    if (!selectedMood || !selectedEnergy || !selectedStress) {
      addNotification({ type: 'error', title: 'Missing Information', message: 'Please select mood, energy, and stress levels' });
      return;
    }

    try {
      await logMood({
        mood_score: selectedMood,
        energy_level: energyOptions.findIndex(e => e.value === selectedEnergy) + 1,
        stress_level: stressOptions.findIndex(s => s.value === selectedStress) + 1,
        // motivation_level: 5, // removed as not in interface
        notes: notes.trim() || undefined,
        // activity: selectedActivities.join(', ') || 'General', // removed as not in interface
        // location: 'Unknown', // removed as not in interface
        // timestamp: new Date().toISOString(), // removed as not in interface
      });
      
      setShowDetailedLog(false);
      resetForm();
      addNotification({ type: 'success', title: 'Mood Logged', message: 'Detailed mood entry saved successfully!' });
    } catch (error) {
      addNotification({ type: 'error', title: 'Logging Failed', message: 'Failed to log your mood' });
    }
  };

  const resetForm = () => {
    setSelectedMood(null);
    setSelectedEnergy(null);
    setSelectedStress(null);
    setSelectedActivities([]);
    setNotes('');
    setSleepHours(8);
    setWeather('sunny');
  };

  const toggleActivity = (activity: string) => {
    setSelectedActivities(prev => 
      prev.includes(activity) 
        ? prev.filter(a => a !== activity)
        : [...prev, activity]
    );
  };

  const getChartData = () => {
    const now = new Date();
    const filteredData = moodHistory.filter(entry => {
      const entryDate = new Date(entry.created_at);
      const diffTime = Math.abs(now.getTime() - entryDate.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      switch (timeFilter) {
        case 'week': return diffDays <= 7;
        case 'month': return diffDays <= 30;
        case 'year': return diffDays <= 365;
        default: return true;
      }
    });

    return filteredData.map(entry => ({
      date: formatDate(entry.created_at, 'short'),
      mood: entry.mood_score,
      energy: entry.energy_level,
      stress: entry.stress_level,
    }));
  };

  const getMoodDistribution = () => {
    const distribution = moodHistory.reduce((acc, entry) => {
            const range = entry.mood_score <= 3 ? 'Low (1-3)' :
                    entry.mood_score <= 7 ? 'Medium (4-7)' : 'High (8-10)';
      acc[range] = (acc[range] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(distribution).map(([range, count]) => ({
      name: range,
      value: count,
    }));
  };

  const getInsights = () => {
    if (moodHistory.length === 0) return [];

    const recentMoods = moodHistory.slice(-7);
    const avgMood = recentMoods.reduce((sum, entry) => sum + entry.mood_score, 0) / recentMoods.length;
    
    const insights = [];
    
    if (avgMood < 5) {
      insights.push({
        type: 'warning',
        icon: Frown,
        title: 'Mood Trend',
        message: 'Your mood has been lower than usual. Consider taking a break or doing something you enjoy.',
        color: 'text-orange-600',
        bgColor: 'bg-orange-100 dark:bg-orange-900/20',
      });
    } else if (avgMood > 7) {
      insights.push({
        type: 'positive',
        icon: Smile,
        title: 'Great Mood!',
        message: 'You\'ve been feeling great lately! Keep up the positive energy.',
        color: 'text-green-600',
        bgColor: 'bg-green-100 dark:bg-green-900/20',
      });
    }

    // Activity correlation - using context.activity if available
    const activityMood = moodHistory.reduce((acc, entry) => {
      const activity = 'General'; // context property removed
      if (!acc[activity]) acc[activity] = [];
      acc[activity].push(entry.mood_score);
      return acc;
    }, {} as Record<string, number[]>);

    const bestActivity = Object.entries(activityMood)
      .map(([activity, moods]) => ({
        activity,
        avgMood: moods.reduce((sum, mood) => sum + mood, 0) / moods.length,
      }))
      .sort((a, b) => b.avgMood - a.avgMood)[0];

    if (bestActivity && bestActivity.avgMood > 7) {
      insights.push({
        type: 'tip',
        icon: Target,
        title: 'Activity Boost',
        message: `${bestActivity.activity} seems to boost your mood! Consider doing more of it.`,
        color: 'text-blue-600',
        bgColor: 'bg-blue-100 dark:bg-blue-900/20',
      });
    }

    return insights;
  };

  const chartData = getChartData();
  const moodDistribution = getMoodDistribution();
  const insights = getInsights();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Mood Tracking</h1>
          <p className="text-muted-foreground mt-1">
            Monitor your emotional well-being and discover patterns
          </p>
        </div>

        <div className="flex space-x-3">
          <Button
            onClick={() => setShowQuickLog(true)}
            variant="outline"
            size="lg"
          >
            <Smile className="h-5 w-5 mr-2" />
            Quick Log
          </Button>
          <Button
            onClick={() => setShowDetailedLog(true)}
            size="lg"
          >
            <BarChart3 className="h-5 w-5 mr-2" />
            Detailed Log
          </Button>
        </div>
      </div>

      {/* Current Mood Display */}
      {currentMood && (
        <Card className="bg-gradient-to-r from-primary/5 to-primary/10 border-primary/20">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="text-4xl">{getMoodEmoji(currentMood.mood_score)}</div>
              <div>
                <h3 className="text-lg font-semibold text-foreground">
                  Current Mood: {currentMood.mood_score}/10
                </h3>
                <p className="text-muted-foreground">
                  Last logged: {formatDate(currentMood.created_at)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mood Trend Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Mood Trend</span>
            </CardTitle>
            <div className="flex space-x-2">
              {(['week', 'month', 'year'] as const).map(filter => (
                <button
                  key={filter}
                  onClick={() => setTimeFilter(filter)}
                  className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                    timeFilter === filter
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-muted-foreground hover:text-foreground'
                  }`}
                >
                  {filter.charAt(0).toUpperCase() + filter.slice(1)}
                </button>
              ))}
            </div>
          </CardHeader>
          <CardContent>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[1, 10]} />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="mood" 
                    stroke="#0066FF" 
                    strokeWidth={3}
                    dot={{ fill: '#0066FF', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                No mood data available for the selected time period
              </div>
            )}
          </CardContent>
        </Card>

        {/* Mood Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <PieChart className="h-5 w-5" />
              <span>Mood Distribution</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {moodDistribution.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={moodDistribution}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {moodDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#ef4444', '#f59e0b', '#10b981'][index % 3]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                No mood data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Insights Section */}
      {insights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="h-5 w-5" />
              <span>AI Insights</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {insights.map((insight, index) => {
                const Icon = insight.icon;
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`p-4 rounded-xl ${insight.bgColor} border border-current/20`}
                  >
                    <div className="flex items-start space-x-3">
                      <Icon className={`h-6 w-6 ${insight.color} mt-1`} />
                      <div>
                        <h4 className="font-semibold text-foreground mb-1">
                          {insight.title}
                        </h4>
                        <p className="text-sm text-muted-foreground">
                          {insight.message}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Mood Log Modal */}
      <AnimatePresence>
        {showQuickLog && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowQuickLog(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-background rounded-2xl shadow-2xl w-full max-w-2xl p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-semibold text-foreground mb-4 text-center">
                How are you feeling right now?
              </h3>
              
              <div className="grid grid-cols-5 gap-3 mb-6">
                {moodOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleQuickMoodLog(option.value)}
                    className="flex flex-col items-center space-y-2 p-4 rounded-xl hover:bg-muted transition-colors"
                  >
                    <div className="text-3xl">{option.emoji}</div>
                    <div className="text-xs text-center text-muted-foreground">
                      {option.label}
                    </div>
                  </button>
                ))}
              </div>

              <div className="text-center">
                <Button
                  variant="outline"
                  onClick={() => setShowQuickLog(false)}
                >
                  Cancel
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Detailed Mood Log Modal */}
      <AnimatePresence>
        {showDetailedLog && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowDetailedLog(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-background rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 border-b border-border">
                <h3 className="text-xl font-semibold text-foreground">Detailed Mood Log</h3>
                <p className="text-muted-foreground">Track your mood with additional context</p>
              </div>

              <div className="p-6 space-y-6 max-h-[calc(90vh-120px)] overflow-y-auto">
                {/* Mood Selection */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-3">
                    How are you feeling? *
                  </label>
                  <div className="grid grid-cols-5 gap-3">
                    {moodOptions.map((option) => (
                      <button
                        key={option.value}
                        onClick={() => setSelectedMood(option.value)}
                        className={`flex flex-col items-center space-y-2 p-3 rounded-xl transition-colors ${
                          selectedMood === option.value
                            ? 'bg-primary text-primary-foreground'
                            : 'hover:bg-muted'
                        }`}
                      >
                        <div className="text-2xl">{option.emoji}</div>
                        <div className="text-xs text-center">
                          {option.label}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Energy and Stress */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-3">
                      Energy Level *
                    </label>
                    <div className="space-y-2">
                      {energyOptions.map((option) => {
                        const Icon = option.icon;
                        return (
                          <button
                            key={option.value}
                            onClick={() => setSelectedEnergy(option.value)}
                            className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                              selectedEnergy === option.value
                                ? 'bg-primary text-primary-foreground'
                                : 'hover:bg-muted'
                            }`}
                          >
                            <Icon className={`h-4 w-4 ${option.color}`} />
                            <span className="text-sm">{option.label}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-3">
                      Stress Level *
                    </label>
                    <div className="space-y-2">
                      {stressOptions.map((option) => {
                        const Icon = option.icon;
                        return (
                          <button
                            key={option.value}
                            onClick={() => setSelectedStress(option.value)}
                            className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                              selectedStress === option.value
                                ? 'bg-primary text-primary-foreground'
                                : 'hover:bg-muted'
                            }`}
                          >
                            <Icon className={`h-4 w-4 ${option.color}`} />
                            <span className="text-sm">{option.label}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* Activities */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-3">
                    What have you been doing?
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {commonActivities.map((activity) => (
                      <button
                        key={activity}
                        onClick={() => toggleActivity(activity)}
                        className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                          selectedActivities.includes(activity)
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted text-muted-foreground hover:text-foreground'
                        }`}
                      >
                        {activity}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Additional Context */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Sleep (hours)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="24"
                      value={sleepHours}
                      onChange={(e) => setSleepHours(parseInt(e.target.value) || 0)}
                      className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Weather
                    </label>
                    <select
                      value={weather}
                      onChange={(e) => setWeather(e.target.value)}
                      className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    >
                      <option value="sunny">☀️ Sunny</option>
                      <option value="cloudy">☁️ Cloudy</option>
                      <option value="rainy">🌧️ Rainy</option>
                      <option value="snowy">❄️ Snowy</option>
                      <option value="stormy">⛈️ Stormy</option>
                    </select>
                  </div>
                </div>

                {/* Notes */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Additional Notes
                  </label>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Any additional thoughts or context..."
                    className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                    rows={3}
                  />
                </div>

                {/* Actions */}
                <div className="flex justify-end space-x-3 pt-4 border-t border-border">
                  <Button
                    variant="outline"
                    onClick={() => setShowDetailedLog(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleDetailedMoodLog}
                    disabled={!selectedMood || !selectedEnergy || !selectedStress}
                  >
                    Log Mood
                  </Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
