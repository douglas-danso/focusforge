import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useStoreStore } from '@/stores/useStoreStore';

const rewardItems = [
  {
    id: 1,
    emoji: '☕',
    name: 'Coffee Break',
    description: 'Take a 15-minute coffee break',
    cost: 50,
    gradient: 'gradient-purple',
  },
  {
    id: 2,
    emoji: '🎮',
    name: 'Gaming Session',
    description: '30 minutes of gaming time',
    cost: 100,
    gradient: 'gradient-green',
  },
  {
    id: 3,
    emoji: '🍕',
    name: 'Pizza Night',
    description: 'Order your favorite pizza',
    cost: 300,
    gradient: 'gradient-orange',
  },
  {
    id: 4,
    emoji: '🎬',
    name: 'Movie Night',
    description: 'Watch a movie of your choice',
    cost: 200,
    gradient: 'gradient-pink',
  },
  {
    id: 5,
    emoji: '📚',
    name: 'Reading Time',
    description: '1 hour of guilt-free reading',
    cost: 75,
    gradient: 'gradient-blue',
  },
  {
    id: 6,
    emoji: '🎵',
    name: 'Concert Ticket',
    description: 'Go to a live concert',
    cost: 500,
    gradient: 'gradient-purple',
  },
  {
    id: 7,
    emoji: '🏋️',
    name: 'Gym Session',
    description: 'Premium gym access for a day',
    cost: 150,
    gradient: 'gradient-green',
  },
  {
    id: 8,
    emoji: '🍰',
    name: 'Dessert Treat',
    description: 'Your favorite dessert',
    cost: 120,
    gradient: 'gradient-pink',
  },
];

export default function Store() {
  const { userProfile, fetchUserProfile } = useStoreStore();

  useEffect(() => {
    fetchUserProfile();
  }, [fetchUserProfile]);

  const points = userProfile?.currency_balance || 0;

  const handleRedeem = (item: typeof rewardItems[0]) => {
    if (points >= item.cost) {
      // TODO: Implement redemption logic
      alert(`Redeemed: ${item.name}!`);
    } else {
      alert('Not enough points!');
    }
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
            Rewards Store
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Redeem your points for awesome rewards
          </p>
        </div>
        <div className="bg-gradient-to-r from-orange-500 to-pink-500 text-white px-6 py-3 rounded-full font-bold text-lg shadow-lg">
          🪙 {points} Points
        </div>
      </motion.div>

      {/* Rewards Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {rewardItems.map((item, idx) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + idx * 0.05 }}
          >
            <Card className="p-6 hover:shadow-xl transition-all cursor-pointer group">
              <div className={`h-32 ${item.gradient} rounded-xl mb-4 flex items-center justify-center text-6xl transition-transform group-hover:scale-110`}>
                {item.emoji}
              </div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2">
                {item.name}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 min-h-[40px]">
                {item.description}
              </p>
              <div className="flex items-center justify-between">
                <span className="text-lg font-bold text-orange-600 dark:text-orange-400">
                  {item.cost} Points
                </span>
                <Button
                  size="sm"
                  onClick={() => handleRedeem(item)}
                  disabled={points < item.cost}
                  className="transition-all"
                >
                  Redeem
                </Button>
              </div>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      {/* AI Recommendations */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card className="p-6 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-2 border-blue-200 dark:border-blue-800">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-3xl">🤖</span>
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              AI Recommendations
            </h3>
          </div>
          <p className="text-gray-700 dark:text-gray-300 mb-4">
            Based on your productivity patterns, you've earned these rewards:
          </p>
          <div className="flex flex-wrap gap-3">
            <div className="px-5 py-3 bg-white dark:bg-gray-800 rounded-xl border-2 border-green-500 flex items-center gap-2">
              <span className="text-2xl">⭐</span>
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                Productivity Master
              </span>
            </div>
            <div className="px-5 py-3 bg-white dark:bg-gray-800 rounded-xl border-2 border-primary-500 flex items-center gap-2">
              <span className="text-2xl">🔥</span>
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                12-Day Streak
              </span>
            </div>
            <div className="px-5 py-3 bg-white dark:bg-gray-800 rounded-xl border-2 border-purple-500 flex items-center gap-2">
              <span className="text-2xl">🏆</span>
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                Focus Champion
              </span>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Points History */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="p-6">
          <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            Recent Transactions
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-xl">
              <div className="flex items-center gap-3">
                <span className="text-2xl">✅</span>
                <div>
                  <div className="font-medium text-gray-900 dark:text-gray-100">
                    Completed 5 tasks
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    2 hours ago
                  </div>
                </div>
              </div>
              <span className="text-green-600 dark:text-green-400 font-semibold">
                +50 pts
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-xl">
              <div className="flex items-center gap-3">
                <span className="text-2xl">🍅</span>
                <div>
                  <div className="font-medium text-gray-900 dark:text-gray-100">
                    Completed focus session
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    5 hours ago
                  </div>
                </div>
              </div>
              <span className="text-green-600 dark:text-green-400 font-semibold">
                +25 pts
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-xl">
              <div className="flex items-center gap-3">
                <span className="text-2xl">🔥</span>
                <div>
                  <div className="font-medium text-gray-900 dark:text-gray-100">
                    Maintained streak
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Yesterday
                  </div>
                </div>
              </div>
              <span className="text-green-600 dark:text-green-400 font-semibold">
                +100 pts
              </span>
            </div>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
