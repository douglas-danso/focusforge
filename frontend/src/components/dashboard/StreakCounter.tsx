import React from 'react';
import { motion } from 'framer-motion';
import { Flame, Trophy, Calendar } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

interface StreakCounterProps {
  streak: number;
}

export default function StreakCounter({ streak }: StreakCounterProps) {
  const getStreakMessage = () => {
    if (streak === 0) return 'Start your streak today! 🚀';
    if (streak === 1) return 'Great start! Keep it going! 💪';
    if (streak < 7) return 'Building momentum! 🔥';
    if (streak < 30) return 'You\'re on fire! 🌟';
    return 'Legendary streak! 👑';
  };

  const getStreakLevel = () => {
    if (streak < 3) return 'Beginner';
    if (streak < 7) return 'Getting Started';
    if (streak < 21) return 'Consistent';
    if (streak < 50) return 'Dedicated';
    return 'Master';
  };

  return (
    <Card>
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center space-x-2 text-lg">
          <Flame className="h-5 w-5 text-orange-500" />
          <span>Streak</span>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Main streak display */}
        <div className="text-center space-y-2">
          <motion.div
            key={streak}
            initial={{ scale: 1.2, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="space-y-1"
          >
            <div className="text-4xl font-bold text-orange-500">
              {streak}
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {streak === 1 ? 'day' : 'days'} in a row
            </p>
          </motion.div>

          <motion.p
            key={getStreakMessage()}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-xs font-medium text-gray-900 dark:text-gray-100"
          >
            {getStreakMessage()}
          </motion.p>
        </div>

        {/* Level indicator */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-gray-600 dark:text-gray-400">Level</span>
            <span className="font-medium text-gray-900 dark:text-gray-100">{getStreakLevel()}</span>
          </div>
          
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <motion.div
              className="bg-orange-500 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${Math.min((streak % 7) / 7 * 100, 100)}%` }}
              transition={{ duration: 1 }}
            />
          </div>
          
          <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400">
            <span>{streak % 7} / 7</span>
            <span>Next level</span>
          </div>
        </div>

        {/* Streak milestones */}
        <div className="space-y-2">
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className={`p-2 rounded-lg ${streak >= 7 ? 'bg-orange-100 dark:bg-orange-900/20' : 'bg-gray-200 dark:bg-gray-700'}`}>
              <Calendar className={`h-4 w-4 mx-auto mb-1 ${streak >= 7 ? 'text-orange-600 dark:text-orange-400' : 'text-gray-600 dark:text-gray-400'}`} />
              <p className="text-xs font-medium">7 Day</p>
            </div>
            
            <div className={`p-2 rounded-lg ${streak >= 30 ? 'bg-orange-100 dark:bg-orange-900/20' : 'bg-gray-200 dark:bg-gray-700'}`}>
              <Trophy className={`h-4 w-4 mx-auto mb-1 ${streak >= 30 ? 'text-orange-600 dark:text-orange-400' : 'text-gray-600 dark:text-gray-400'}`} />
              <p className="text-xs font-medium">30 Day</p>
            </div>
            
            <div className={`p-2 rounded-lg ${streak >= 100 ? 'bg-orange-100 dark:bg-orange-900/20' : 'bg-gray-200 dark:bg-gray-700'}`}>
              <Flame className={`h-4 w-4 mx-auto mb-1 ${streak >= 100 ? 'text-orange-600 dark:text-orange-400' : 'text-gray-600 dark:text-gray-400'}`} />
              <p className="text-xs font-medium">100 Day</p>
            </div>
          </div>
        </div>

        {/* Streak tip */}
        <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-center text-gray-600 dark:text-gray-400">
            💡 Complete at least one task daily to maintain your streak
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
