import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useTaskStore } from '../stores/useTaskStore';
import { useStoreStore } from '../stores/useStoreStore';
import { analyticsAPI, orchestratorAPI, moodAPI } from '../services/api';

interface AIInsight {
  type: string;
  title: string;
  description: string;
  action?: string;
  priority?: string;
}

interface ProductivityAnalytics {
  total_focus_time?: number;
  tasks_completed?: number;
  completion_rate?: number;
  productivity_trends?: any[];
}

export default function Analytics() {
  const { tasks } = useTaskStore();
  const { userProfile } = useStoreStore();
  const [productivityData, setProductivityData] = useState<ProductivityAnalytics | null>(null);
  const [aiInsights, setAiInsights] = useState<AIInsight[]>([]);
  const [moodCorrelation, setMoodCorrelation] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [timePeriod, setTimePeriod] = useState<'day' | 'week' | 'month'>('week');

  useEffect(() => {
    loadAnalytics();
  }, [timePeriod]);

  const loadAnalytics = async () => {
    setIsLoading(true);
    try {
      const [productivityRes, moodCorrelationRes, optimizationRes] = await Promise.all([
        analyticsAPI.getProductivityAnalytics({ period: timePeriod }),
        analyticsAPI.getMoodCorrelationAnalytics(),
        orchestratorAPI.getDailyOptimization(),
      ]);

      if (productivityRes.data) {
        setProductivityData(productivityRes.data);
      }

      if (moodCorrelationRes.data) {
        setMoodCorrelation(moodCorrelationRes.data);
      }

      // Convert optimization insights to AI insights format
      if (optimizationRes.data?.insights) {
        const insights: AIInsight[] = optimizationRes.data.insights.map((insight: string, idx: number) => ({
          type: idx === 0 ? 'performance' : idx === 1 ? 'pattern' : 'mood',
          title: idx === 0 ? 'Peak Performance Hours' : idx === 1 ? 'Task Pattern Recognition' : 'Mood & Productivity Correlation',
          description: insight,
          action: 'View Recommendations',
          priority: 'high',
        }));
        setAiInsights(insights);
      }
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate some basic stats
  const completedTasks = productivityData?.tasks_completed || tasks.filter(t => t.status === 'completed').length;
  const totalTasks = tasks.length;
  const completionRate = productivityData?.completion_rate || (totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0);

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
            Analytics & Insights
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Track your productivity and growth
          </p>
        </div>
        <div>
          <select
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            value={timePeriod}
            onChange={(e) => setTimePeriod(e.target.value as 'day' | 'week' | 'month')}
          >
            <option value="day">Last 24 hours</option>
            <option value="week">Last 7 days</option>
            <option value="month">Last 30 days</option>
          </select>
        </div>
      </motion.div>

      {/* Stats Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        <Card className="p-6 gradient-purple text-white">
          <div className="text-sm font-medium opacity-80 mb-2">Total Focus Time</div>
          {isLoading ? (
            <div className="animate-pulse">
              <div className="h-10 bg-white/20 rounded w-32 mb-1"></div>
              <div className="h-4 bg-white/20 rounded w-24"></div>
            </div>
          ) : (
            <>
              <div className="text-4xl font-bold mb-1">
                {productivityData?.total_focus_time
                  ? `${Math.floor(productivityData.total_focus_time / 60)}h ${productivityData.total_focus_time % 60}m`
                  : '0h 0m'}
              </div>
              <div className="text-sm opacity-90">Keep it up!</div>
            </>
          )}
        </Card>

        <Card className="p-6 gradient-blue text-white">
          <div className="text-sm font-medium opacity-80 mb-2">Tasks Completed</div>
          {isLoading ? (
            <div className="animate-pulse">
              <div className="h-10 bg-white/20 rounded w-20 mb-1"></div>
              <div className="h-4 bg-white/20 rounded w-32"></div>
            </div>
          ) : (
            <>
              <div className="text-4xl font-bold mb-1">{completedTasks}</div>
              <div className="text-sm opacity-90">{completionRate}% completion rate</div>
            </>
          )}
        </Card>

        <Card className="p-6 gradient-green text-white">
          <div className="text-sm font-medium opacity-80 mb-2">Current Streak</div>
          <div className="text-4xl font-bold mb-1">{userProfile?.streak_count || 0} days</div>
          <div className="text-sm opacity-90">🔥 Keep going!</div>
        </Card>
      </motion.div>

      {/* Productivity Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              Daily Productivity Trend
            </h2>
            <div className="flex gap-2">
              <Button variant="secondary" size="sm">Tasks</Button>
              <Button size="sm">Focus Time</Button>
              <Button variant="secondary" size="sm">Points</Button>
            </div>
          </div>

          <div className="h-80 bg-gray-100 dark:bg-gray-800 rounded-xl flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-4">📊</div>
              <p className="text-gray-600 dark:text-gray-400">
                Interactive chart showing productivity trends
              </p>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* AI Insights */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <span className="text-3xl">🤖</span>
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              AI-Powered Insights
            </h2>
          </div>

          <div className="space-y-4">
            {isLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="p-4 bg-gray-100 dark:bg-gray-800 rounded-xl animate-pulse">
                    <div className="h-6 bg-gray-300 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
                    <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-full mb-2"></div>
                    <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-2/3"></div>
                  </div>
                ))}
              </div>
            ) : aiInsights.length > 0 ? (
              aiInsights.map((insight, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-xl border-l-4 ${
                    idx === 0
                      ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-500'
                      : idx === 1
                      ? 'bg-purple-50 dark:bg-purple-900/20 border-purple-500'
                      : 'bg-green-50 dark:bg-green-900/20 border-green-500'
                  }`}
                >
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                    {insight.title}
                  </h3>
                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                    {insight.description}
                  </p>
                  {insight.action && (
                    <Button size="sm" variant="secondary">{insight.action}</Button>
                  )}
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                <p>Keep using FocusForge to unlock AI-powered insights!</p>
              </div>
            )}
          </div>
        </Card>
      </motion.div>

      {/* Category Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              Tasks by Category
            </h2>
            <div className="h-64 bg-gray-100 dark:bg-gray-800 rounded-xl flex items-center justify-center">
              <div className="text-center">
                <div className="text-5xl mb-2">📈</div>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Category distribution chart
                </p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              Weekly Activity
            </h2>
            <div className="h-64 bg-gray-100 dark:bg-gray-800 rounded-xl flex items-center justify-center">
              <div className="text-center">
                <div className="text-5xl mb-2">📊</div>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Weekly activity heatmap
                </p>
              </div>
            </div>
          </Card>
        </div>
      </motion.div>
    </div>
  );
}
