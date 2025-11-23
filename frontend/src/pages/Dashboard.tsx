import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Plus } from 'lucide-react';
import { useAuthStore } from '../stores/useAuthStore';
import { useTaskStore } from '../stores/useTaskStore';
import { useStoreStore } from '../stores/useStoreStore';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { useNavigate } from 'react-router-dom';
import { orchestratorAPI, analyticsAPI } from '../services/api';

interface DailyOptimization {
  recommended_tasks?: any[];
  insights?: string[];
  optimal_schedule?: any[];
  productivity_score?: number;
}

export default function Dashboard() {
  const { user } = useAuthStore();
  const { tasks, fetchDashboardTasks } = useTaskStore();
  const { userProfile, fetchUserProfile } = useStoreStore();
  const navigate = useNavigate();
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [dailyOptimization, setDailyOptimization] = useState<DailyOptimization | null>(null);
  const [aiTip, setAiTip] = useState<string>('Loading AI insights...');
  const [isLoadingAI, setIsLoadingAI] = useState(true);

  useEffect(() => {
    // Load dashboard data on mount
    const loadDashboardData = async () => {
      try {
        await Promise.all([
          fetchDashboardTasks(),
          fetchUserProfile(),
          loadAIOptimization(),
        ]);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      }
    };

    loadDashboardData();
  }, [fetchDashboardTasks, fetchUserProfile]);

  const loadAIOptimization = async () => {
    setIsLoadingAI(true);
    try {
      // Fetch AI daily optimization from orchestrator
      const optimizationResponse = await orchestratorAPI.getDailyOptimization();
      if (optimizationResponse.data) {
        setDailyOptimization(optimizationResponse.data);

        // Set AI tip from insights
        if (optimizationResponse.data.insights && optimizationResponse.data.insights.length > 0) {
          setAiTip(optimizationResponse.data.insights[0]);
        }
      }
    } catch (error) {
      console.error('Failed to load AI optimization:', error);
      setAiTip('AI insights temporarily unavailable. Keep up the great work!');
    } finally {
      setIsLoadingAI(false);
    }
  };

  const todayTasks = tasks.filter(task => {
    const today = new Date().toDateString();
    return new Date(task.created_at).toDateString() === today;
  });

  const completedTasks = todayTasks.filter(task => task.status === 'completed').length;
  const totalTasks = todayTasks.length;
  const streakCount = userProfile?.streak_count || 0;
  const points = userProfile?.currency_balance || 0;

  const getTimeOfDay = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'morning';
    if (hour < 17) return 'afternoon';
    return 'evening';
  };

  const priorityStyles = {
    high: 'bg-pink-500',
    medium: 'bg-orange-500',
    low: 'bg-green-500'
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
      >
        <div>
          <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">
            Welcome back, {user?.name?.split(' ')[0]}! 👋
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {getTimeOfDay() === 'morning' && 'Ready to conquer your day?'}
            {getTimeOfDay() === 'afternoon' && 'Keep up the great work!'}
            {getTimeOfDay() === 'evening' && 'Time to wrap up your day!'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={() => navigate('/calendar')}
            variant="secondary"
            className="gap-2"
          >
            📅 Today
          </Button>
          <Button
            onClick={() => setShowTaskModal(true)}
            className="gap-2"
          >
            <Plus className="h-5 w-5" />
            New Task
          </Button>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="text-sm text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
            Tasks Completed Today
          </div>
          <div className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">
            {completedTasks}
          </div>
          <div className="text-sm text-green-600 dark:text-green-400 flex items-center gap-1">
            ↑ 33% from yesterday
          </div>
        </Card>

        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="text-sm text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
            Current Streak
          </div>
          <div className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">
            {streakCount}
          </div>
          <div className="text-sm text-orange-600 dark:text-orange-400 flex items-center gap-1">
            🔥 Keep going!
          </div>
        </Card>

        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="text-sm text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
            Focus Time
          </div>
          <div className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">
            4.5h
          </div>
          <div className="text-sm text-green-600 dark:text-green-400 flex items-center gap-1">
            ↑ 1.2h from average
          </div>
        </Card>

        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="text-sm text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
            Reward Points
          </div>
          <div className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">
            {points}
          </div>
          <div className="text-sm text-green-600 dark:text-green-400 flex items-center gap-1">
            +50 earned today
          </div>
        </Card>
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left Column - 2/3 width */}
        <div className="lg:col-span-2 space-y-6">
          {/* Pomodoro Timer Widget */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="p-8 bg-gradient-purple text-white overflow-hidden relative">
              <div className="relative z-10">
                <h3 className="text-lg font-semibold mb-4 opacity-90">
                  Current Focus Session
                </h3>
                <div className="text-7xl font-bold mb-6 font-mono tracking-tight">
                  25:00
                </div>
                <p className="text-lg mb-6 opacity-90">
                  Ready to start focusing?
                </p>
                <div className="flex gap-4 items-center">
                  <button className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm border-2 border-white flex items-center justify-center hover:bg-white/30 transition-all text-2xl">
                    ▶️
                  </button>
                  <button className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm border-2 border-white flex items-center justify-center hover:bg-white/30 transition-all text-2xl">
                    ⏹️
                  </button>
                </div>
              </div>
            </Card>
          </motion.div>

          {/* Today's Tasks */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  Today's Tasks
                </h2>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => navigate('/tasks')}
                >
                  View All
                </Button>
              </div>

              <div className="space-y-3">
                {todayTasks.length === 0 ? (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    <p className="text-lg mb-2">No tasks for today yet!</p>
                    <p className="text-sm">Create your first task to get started</p>
                  </div>
                ) : (
                  todayTasks.slice(0, 3).map((task) => (
                    <div
                      key={task.id}
                      className="flex items-start gap-4 p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:shadow-md transition-all cursor-pointer"
                      onClick={() => navigate(`/tasks/${task.id}`)}
                    >
                      <div
                        className={`w-1 h-12 rounded-full ${priorityStyles[task.priority as keyof typeof priorityStyles] || 'bg-gray-400'}`}
                      />
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">
                          {task.title}
                        </h3>
                        {task.description && (
                          <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-1">
                            {task.description}
                          </p>
                        )}
                        <div className="flex items-center gap-4 mt-3 text-xs text-gray-500 dark:text-gray-400">
                          <span className="flex items-center gap-1">
                            🕐 {task.duration_minutes || 25} mins
                          </span>
                          <span className="flex items-center gap-1">
                            🏷️ {task.category}
                          </span>
                          {task.pomodoro_blocks && task.pomodoro_blocks.length > 0 && (
                            <span className="flex items-center gap-1">
                              🍅 {task.pomodoro_blocks.length} sessions
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </motion.div>

          {/* Weekly Progress */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  Weekly Progress
                </h2>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  75% Complete
                </span>
              </div>
              <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden mb-2">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all"
                  style={{ width: '75%' }}
                />
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                15 of 20 tasks completed this week
              </p>
            </Card>
          </motion.div>
        </div>

        {/* Right Column - 1/3 width */}
        <div className="space-y-6">
          {/* AI Tip Card */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="p-6 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-2 border-blue-200 dark:border-blue-800">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">🤖</span>
                <h3 className="font-bold text-gray-900 dark:text-gray-100">
                  AI Insight
                </h3>
              </div>
              {isLoadingAI ? (
                <div className="flex items-center justify-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500"></div>
                </div>
              ) : (
                <>
                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">
                    {aiTip}
                  </p>
                  {dailyOptimization?.productivity_score && (
                    <div className="mb-4 p-3 bg-white dark:bg-gray-800 rounded-xl">
                      <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                        Today's Productivity Score
                      </div>
                      <div className="text-2xl font-bold text-primary-500">
                        {Math.round(dailyOptimization.productivity_score * 100)}%
                      </div>
                    </div>
                  )}
                  <Button
                    size="sm"
                    variant="secondary"
                    className="w-full"
                    onClick={() => navigate('/analytics')}
                  >
                    View All Insights
                  </Button>
                </>
              )}
            </Card>
          </motion.div>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="p-6">
              <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">
                Quick Actions
              </h3>
              <div className="space-y-2">
                <button
                  onClick={() => navigate('/focus')}
                  className="w-full p-3 bg-primary-500 hover:bg-primary-600 text-white rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
                >
                  🍅 Start Focus Session
                </button>
                <button
                  onClick={() => navigate('/mood')}
                  className="w-full p-3 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
                >
                  😊 Log Mood
                </button>
                <button
                  onClick={() => navigate('/store')}
                  className="w-full p-3 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
                >
                  🏆 View Rewards
                </button>
              </div>
            </Card>
          </motion.div>

          {/* Mood Check */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="p-6">
              <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">
                How are you feeling?
              </h3>
              <div className="flex justify-between gap-2 mb-4">
                {['😔', '😐', '😊', '😄', '🤩'].map((emoji, idx) => (
                  <button
                    key={idx}
                    className="flex-1 aspect-square rounded-xl bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-all text-3xl flex items-center justify-center hover:scale-110"
                    onClick={() => navigate('/mood')}
                  >
                    {emoji}
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                Track your mood to optimize productivity
              </p>
            </Card>
          </motion.div>
        </div>
      </div>

      {/* Floating Action Button - Mobile */}
      <button
        onClick={() => setShowTaskModal(true)}
        className="lg:hidden fixed bottom-20 right-6 w-14 h-14 bg-primary-500 hover:bg-primary-600 text-white rounded-full shadow-lg flex items-center justify-center z-40 transition-all hover:scale-110"
      >
        <Plus className="h-6 w-6" />
      </button>
    </div>
  );
}
