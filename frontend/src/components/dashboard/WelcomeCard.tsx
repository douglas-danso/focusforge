import React from 'react';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../stores/useAuthStore';
import { useUserProfile } from '../../stores/useStoreStore';
import { Card } from '../ui/Card';
import { formatDate } from '../../lib/utils';

export const WelcomeCard: React.FC = () => {
  const { user } = useAuthStore();
  const userProfile = useUserProfile();

  if (!user) {
    return (
      <Card className="p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </Card>
    );
  }

  const currentTime = new Date();
  const hour = currentTime.getHours();
  
  let greeting = 'Good morning';
  if (hour >= 12 && hour < 17) {
    greeting = 'Good afternoon';
  } else if (hour >= 17) {
    greeting = 'Good evening';
  }

  const stats = {
    streak: userProfile?.streak_count || 0,
    level: userProfile?.level || 1,
    tasksCompleted: userProfile?.total_earned ? Math.floor(userProfile.total_earned / 10) : 0,
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="p-6 bg-gradient-to-br from-blue-50 to-indigo-100 border-blue-200">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <motion.h1
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-2xl font-bold text-gray-900"
            >
              {greeting}, {user.name}! 👋
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-gray-600"
            >
              Today is {formatDate(currentTime, 'full')}. Ready to be productive?
            </motion.p>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="text-right space-y-1"
          >
            <div className="text-sm text-gray-600">Level {stats.level}</div>
            <div className="text-xs text-gray-500">
              {stats.tasksCompleted} tasks completed
            </div>
          </motion.div>
        </div>

        {stats.streak > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="mt-4 flex items-center space-x-2 text-sm text-orange-600 bg-orange-50 px-3 py-2 rounded-lg"
          >
            <span className="text-lg">🔥</span>
            <span className="font-medium">{stats.streak} day streak!</span>
            <span className="text-orange-500">Keep it up!</span>
          </motion.div>
        )}
      </Card>
    </motion.div>
  );
};
