import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, TrendingUp, Flame, Brain, Clock, Target } from 'lucide-react';
import { useAuthStore } from '../stores/useAuthStore';
import { useTaskStore } from '../stores/useTaskStore';
import { useStoreStore } from '../stores/useStoreStore';
import { useMoodStore, useMoodComputed } from '../stores/useMoodStore';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { WelcomeCard } from '../components/dashboard/WelcomeCard';
import { CurrencyDisplay } from '../components/dashboard/CurrencyDisplay';
import ProgressRing from '../components/dashboard/ProgressRing';
import { MoodCheckCard } from '../components/dashboard/MoodCheckCard';
import TasksPreview from '@/components/dashboard/TasksPreview';
import AITipCard from '@/components/dashboard/AITipCard';
import StreakCounter from '@/components/dashboard/StreakCounter';
import FocusSessionCard from '@/components/dashboard/FocusSessionCard';

export default function Dashboard() {
  const { user } = useAuthStore();
  const { fetchDashboardTasks } = useTaskStore();
  const { fetchUserProfile, userProfile } = useStoreStore();
  const { fetchMoodHistory } = useMoodStore();
  const { getAverageMood, getMoodTrend } = useMoodComputed();

  useEffect(() => {
    // Load dashboard data on mount
    const loadDashboardData = async () => {
      try {
        await Promise.all([
          fetchDashboardTasks(),
          fetchUserProfile(),
          fetchMoodHistory(), // Last 7 days
        ]);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      }
    };

    loadDashboardData();
  }, [fetchDashboardTasks, fetchUserProfile, fetchMoodHistory]);

  const stats = {
    tasksCompleted: 0, // Will be populated from task store
    totalTasks: 0, // Will be populated from task store 
    focusTime: 0, // Will be populated from task store
    streak: userProfile?.streak_count || 0,
    averageMood: getAverageMood(7),
    moodTrend: getMoodTrend(),
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Good {getTimeOfDay()}, {user?.name?.split(' ')[0]}! 👋
          </h1>
          <p className="text-muted-foreground mt-1">
            Ready to make today productive?
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <CurrencyDisplay />
          <Button size="lg">
            <Plus className="h-5 w-5 mr-2" />
            Add Task
          </Button>
        </div>
      </motion.div>

      {/* Quick stats row */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <Target className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Today's Progress</p>
                <p className="text-2xl font-bold text-foreground">
                  {stats.tasksCompleted}/{stats.totalTasks}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center">
                <Clock className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Focus Time</p>
                <p className="text-2xl font-bold text-foreground">
                  {Math.floor(stats.focusTime / 60)}h {stats.focusTime % 60}m
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 rounded-xl bg-orange-100 dark:bg-orange-900/20 flex items-center justify-center">
                <Flame className="h-6 w-6 text-orange-600 dark:text-orange-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Streak</p>
                <p className="text-2xl font-bold text-foreground">
                  {stats.streak} days
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 rounded-xl bg-green-100 dark:bg-green-900/20 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Mood Score</p>
                <p className="text-2xl font-bold text-foreground">
                  {stats.averageMood}/10
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Main dashboard grid */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Welcome and progress */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <WelcomeCard />
          </motion.div>

          {/* Tasks preview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <TasksPreview />
          </motion.div>

          {/* Focus session */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <FocusSessionCard />
          </motion.div>
        </div>

        {/* Right column */}
        <div className="space-y-6">
          {/* Daily progress ring */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <ProgressRing
              completed={stats.tasksCompleted}
              total={stats.totalTasks}
            />
          </motion.div>

          {/* Streak counter */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <StreakCounter streak={stats.streak} />
          </motion.div>

          {/* Mood check */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <MoodCheckCard />
          </motion.div>

          {/* AI tip */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <AITipCard />
          </motion.div>
        </div>
      </div>
    </div>
  );
}

function getTimeOfDay(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'morning';
  if (hour < 17) return 'afternoon';
  return 'evening';
}
