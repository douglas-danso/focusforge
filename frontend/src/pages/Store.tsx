import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Coins, 
  Gift, 
  Trophy, 
  Star, 
  Flame, 
  Target, 
  TrendingUp,
  ShoppingCart,
  Heart,
  Zap,
  Coffee,
  BookOpen,
  Music,
  Gamepad2,
  Utensils,
  Users,
  Award,
  Crown,
  Medal,
  Badge
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useStoreStore, useStoreActions } from '@/stores/useStoreStore';
import { useUIStore } from '@/stores/useUIStore';
import { formatCurrency } from '@/lib/utils';

interface StoreItem {
  id: string;
  name: string;
  description: string;
  category: string;
  cost: number;
  duration?: number; // in minutes
  type: 'rest' | 'entertainment' | 'food' | 'social' | 'wellness' | 'productivity';
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  icon: any;
  mood_boost?: number;
  energy_restore?: number;
  is_recommended?: boolean;
}

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: any;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  unlocked: boolean;
  progress: number;
  max_progress: number;
  reward_currency: number;
}

const storeItems: StoreItem[] = [
  // Rest & Recovery
  {
    id: 'short_break',
    name: 'Short Break',
    description: 'Take a 15-minute break to recharge',
    category: 'Rest',
    cost: 50,
    duration: 15,
    type: 'rest',
    rarity: 'common',
    icon: Coffee,
    mood_boost: 2,
    energy_restore: 3,
  },
  {
    id: 'power_nap',
    name: 'Power Nap',
    description: 'A refreshing 30-minute nap',
    category: 'Rest',
    cost: 100,
    duration: 30,
    type: 'rest',
    rarity: 'rare',
    icon: Coffee,
    mood_boost: 3,
    energy_restore: 5,
  },
  {
    id: 'spa_session',
    name: 'Spa Session',
    description: 'Luxurious 2-hour relaxation session',
    category: 'Rest',
    cost: 500,
    duration: 120,
    type: 'rest',
    rarity: 'epic',
    icon: Heart,
    mood_boost: 5,
    energy_restore: 8,
  },

  // Entertainment
  {
    id: 'movie_time',
    name: 'Movie Time',
    description: 'Watch a movie of your choice',
    category: 'Entertainment',
    cost: 200,
    duration: 120,
    type: 'entertainment',
    rarity: 'rare',
    icon: Gamepad2,
    mood_boost: 4,
    energy_restore: 2,
  },
  {
    id: 'gaming_session',
    name: 'Gaming Session',
    description: '1-hour gaming session',
    category: 'Entertainment',
    cost: 150,
    duration: 60,
    type: 'entertainment',
    rarity: 'common',
    icon: Gamepad2,
    mood_boost: 3,
    energy_restore: 1,
  },
  {
    id: 'concert_ticket',
    name: 'Concert Ticket',
    description: 'Virtual concert experience',
    category: 'Entertainment',
    cost: 800,
    duration: 180,
    type: 'entertainment',
    rarity: 'legendary',
    icon: Music,
    mood_boost: 8,
    energy_restore: 4,
  },

  // Food & Treats
  {
    id: 'coffee_break',
    name: 'Coffee Break',
    description: 'Enjoy a premium coffee',
    category: 'Food',
    cost: 75,
    duration: 20,
    type: 'food',
    rarity: 'common',
    icon: Coffee,
    mood_boost: 2,
    energy_restore: 3,
  },
  {
    id: 'fine_dining',
    name: 'Fine Dining',
    description: 'Luxury dining experience',
    category: 'Food',
    cost: 600,
    duration: 90,
    type: 'food',
    rarity: 'epic',
    icon: Utensils,
    mood_boost: 6,
    energy_restore: 4,
  },

  // Social Activities
  {
    id: 'friend_hangout',
    name: 'Friend Hangout',
    description: 'Spend time with friends',
    category: 'Social',
    cost: 120,
    duration: 60,
    type: 'social',
    rarity: 'common',
    icon: Users,
    mood_boost: 4,
    energy_restore: 2,
  },
  {
    id: 'party_time',
    name: 'Party Time',
    description: 'Host a celebration',
    category: 'Social',
    cost: 400,
    duration: 240,
    type: 'social',
    rarity: 'rare',
    icon: Users,
    mood_boost: 7,
    energy_restore: 3,
  },

  // Wellness
  {
    id: 'meditation',
    name: 'Meditation Session',
    description: 'Guided meditation and mindfulness',
    category: 'Wellness',
    cost: 80,
    duration: 30,
    type: 'wellness',
    rarity: 'common',
    icon: Heart,
    mood_boost: 3,
    energy_restore: 2,
  },
  {
    id: 'yoga_class',
    name: 'Yoga Class',
    description: 'Full yoga session',
    category: 'Wellness',
    cost: 150,
    duration: 60,
    type: 'wellness',
    rarity: 'rare',
    icon: Heart,
    mood_boost: 4,
    energy_restore: 3,
  },

  // Productivity
  {
    id: 'skill_course',
    name: 'Skill Course',
    description: 'Learn a new skill',
    category: 'Productivity',
    cost: 300,
    duration: 480,
    type: 'productivity',
    rarity: 'rare',
    icon: BookOpen,
    mood_boost: 2,
    energy_restore: 1,
  },
  {
    id: 'workshop',
    name: 'Workshop',
    description: 'Attend a professional workshop',
    category: 'Productivity',
    cost: 700,
    duration: 360,
    type: 'productivity',
    rarity: 'epic',
    icon: BookOpen,
    mood_boost: 3,
    energy_restore: 2,
  },
];

const achievements: Achievement[] = [
  {
    id: 'first_task',
    name: 'First Steps',
    description: 'Complete your first task',
    icon: Target,
    rarity: 'common',
    unlocked: true,
    progress: 1,
    max_progress: 1,
    reward_currency: 50,
  },
  {
    id: 'streak_7',
    name: 'Week Warrior',
    description: 'Maintain a 7-day streak',
    icon: Flame,
    rarity: 'rare',
    unlocked: false,
    progress: 3,
    max_progress: 7,
    reward_currency: 200,
  },
  {
    id: 'mood_master',
    name: 'Mood Master',
    description: 'Log mood for 30 consecutive days',
    icon: Heart,
    rarity: 'epic',
    unlocked: false,
    progress: 12,
    max_progress: 30,
    reward_currency: 500,
  },
  {
    id: 'productivity_king',
    name: 'Productivity King',
    description: 'Complete 100 tasks',
    icon: Crown,
    rarity: 'legendary',
    unlocked: false,
    progress: 23,
    max_progress: 100,
    reward_currency: 1000,
  },
];

const categories = [
  { key: 'all', label: 'All', icon: ShoppingCart },
  { key: 'rest', label: 'Rest', icon: Coffee },
  { key: 'entertainment', label: 'Entertainment', icon: Gamepad2 },
  { key: 'food', label: 'Food', icon: Utensils },
  { key: 'social', label: 'Social', icon: Users },
  { key: 'wellness', label: 'Wellness', icon: Heart },
  { key: 'productivity', label: 'Productivity', icon: BookOpen },
];

export default function Store() {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showPurchaseModal, setShowPurchaseModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState<StoreItem | null>(null);
  const [activeTab, setActiveTab] = useState<'store' | 'achievements' | 'profile'>('store');

  const { items, userProfile, activeRewards, getCurrencyBalance, fetchStoreItems, purchaseItem } = useStoreStore();
  const { addNotification } = useUIStore();

  const currency = getCurrencyBalance();

  useEffect(() => {
    fetchStoreItems();
  }, [fetchStoreItems]);

  const filteredItems = storeItems.filter(item => 
    selectedCategory === 'all' || item.type === selectedCategory
  );

  const handlePurchase = async (item: StoreItem) => {
    if (currency < item.cost) {
      addNotification({ type: 'error', title: 'Insufficient Funds', message: `You need ${formatCurrency(item.cost)} to purchase this item` });
      return;
    }

    try {
      await purchaseItem(item.id);
      addNotification({ type: 'success', title: 'Purchase Successful', message: `You've purchased ${item.name}!` });
      setShowPurchaseModal(false);
      setSelectedItem(null);
    } catch (error: any) {
      addNotification({ type: 'error', title: 'Purchase Failed', message: error.message || 'Failed to purchase item' });
    }
  };

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20';
      case 'rare': return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20';
      case 'epic': return 'text-purple-600 bg-purple-100 dark:text-purple-400 dark:bg-purple-900/20';
      case 'legendary': return 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/20';
      default: return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20';
    }
  };

  const getRarityIcon = (rarity: string) => {
    switch (rarity) {
      case 'common': return <Star className="h-3 w-3" />;
      case 'rare': return <Star className="h-3 w-3 fill-current" />;
      case 'epic': return <Award className="h-3 w-3" />;
      case 'legendary': return <Crown className="h-3 w-3" />;
      default: return <Star className="h-3 w-3" />;
    }
  };

  const unlockedAchievements = achievements.filter(a => a.unlocked);
  const lockedAchievements = achievements.filter(a => !a.unlocked);

  return (
    <div className="space-y-6">
      {/* Header with Currency */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Store & Rewards</h1>
          <p className="text-muted-foreground mt-1">
            Spend your earned currency on rewards and experiences
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full p-1">
            <div className="bg-background rounded-full px-4 py-2 flex items-center space-x-2">
              <Coins className="h-5 w-5 text-yellow-600" />
              <span className="font-bold text-lg text-foreground">
                {formatCurrency(currency)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-muted rounded-lg p-1">
        {[
          { key: 'store', label: 'Store', icon: ShoppingCart },
          { key: 'achievements', label: 'Achievements', icon: Trophy },
          { key: 'profile', label: 'Profile', icon: Target },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Store Tab */}
      {activeTab === 'store' && (
        <div className="space-y-6">
          {/* Categories */}
          <div className="flex space-x-2 overflow-x-auto pb-2">
            {categories.map((category) => {
              const Icon = category.icon;
              return (
                <button
                  key={category.key}
                  onClick={() => setSelectedCategory(category.key)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
                    selectedCategory === category.key
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{category.label}</span>
                </button>
              );
            })}
          </div>

          {/* Store Items Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredItems.map((item) => {
              const Icon = item.icon;
              return (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Card className={`h-full transition-all duration-200 ${
                    item.is_recommended ? 'ring-2 ring-primary/50 bg-primary/5' : ''
                  }`}>
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                          <Icon className="h-6 w-6 text-primary" />
                        </div>
                        <div className="flex items-center space-x-1">
                          {getRarityIcon(item.rarity)}
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRarityColor(item.rarity)}`}>
                            {item.rarity}
                          </span>
                        </div>
                      </div>
                      <CardTitle className="text-lg">{item.name}</CardTitle>
                      <p className="text-sm text-muted-foreground">{item.description}</p>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {/* Stats */}
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        {item.mood_boost && (
                          <div className="flex items-center space-x-1">
                            <Heart className="h-4 w-4 text-red-500" />
                            <span>+{item.mood_boost} Mood</span>
                          </div>
                        )}
                        {item.energy_restore && (
                          <div className="flex items-center space-x-1">
                            <Zap className="h-4 w-4 text-yellow-500" />
                            <span>+{item.energy_restore} Energy</span>
                          </div>
                        )}
                        {item.duration && (
                          <div className="flex items-center space-x-1">
                            <Target className="h-4 w-4 text-blue-500" />
                            <span>{item.duration}m</span>
                          </div>
                        )}
                      </div>

                      {/* Price and Purchase */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Coins className="h-4 w-4 text-yellow-600" />
                          <span className="font-bold text-lg">{item.cost}</span>
                        </div>
                        <Button
                          onClick={() => {
                            setSelectedItem(item);
                            setShowPurchaseModal(true);
                          }}
                          disabled={currency < item.cost}
                          size="sm"
                        >
                          Purchase
                        </Button>
                      </div>

                      {item.is_recommended && (
                        <div className="text-center p-2 bg-primary/10 rounded-lg">
                          <span className="text-xs text-primary font-medium">
                            🌟 Recommended for you
                          </span>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      {/* Achievements Tab */}
      {activeTab === 'achievements' && (
        <div className="space-y-6">
          {/* Achievement Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-primary">{unlockedAchievements.length}</div>
                <div className="text-sm text-muted-foreground">Achievements Unlocked</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-green-600">
                  {achievements.reduce((sum, a) => sum + a.reward_currency, 0)}
                </div>
                <div className="text-sm text-muted-foreground">Total Rewards</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round((unlockedAchievements.length / achievements.length) * 100)}%
                </div>
                <div className="text-sm text-muted-foreground">Completion Rate</div>
              </CardContent>
            </Card>
          </div>

          {/* Achievements Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {achievements.map((achievement) => {
              const Icon = achievement.icon;
              return (
                <Card key={achievement.id} className={achievement.unlocked ? 'ring-2 ring-green-500/50' : ''}>
                  <CardContent className="p-4">
                    <div className="flex items-start space-x-3">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                        achievement.unlocked 
                          ? 'bg-green-100 dark:bg-green-900/20' 
                          : 'bg-muted'
                      }`}>
                        <Icon className={`h-6 w-6 ${
                          achievement.unlocked ? 'text-green-600' : 'text-muted-foreground'
                        }`} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <h3 className="font-semibold text-foreground">{achievement.name}</h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRarityColor(achievement.rarity)}`}>
                            {achievement.rarity}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">{achievement.description}</p>
                        
                        {/* Progress Bar */}
                        <div className="space-y-2">
                          <div className="flex justify-between text-xs text-muted-foreground">
                            <span>Progress</span>
                            <span>{achievement.progress}/{achievement.max_progress}</span>
                          </div>
                          <div className="w-full bg-muted rounded-full h-2">
                            <motion.div
                              className={`h-2 rounded-full ${
                                achievement.unlocked ? 'bg-green-500' : 'bg-primary'
                              }`}
                              initial={{ width: 0 }}
                              animate={{ width: `${(achievement.progress / achievement.max_progress) * 100}%` }}
                              transition={{ duration: 0.5 }}
                            />
                          </div>
                        </div>

                        {/* Reward */}
                        <div className="flex items-center justify-between mt-3">
                          <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                            <Coins className="h-3 w-3" />
                            <span>{achievement.reward_currency}</span>
                          </div>
                          {achievement.unlocked && (
                            <div className="text-green-600 text-sm font-medium">
                              ✓ Unlocked
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="space-y-6">
          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-primary">23</div>
                <div className="text-sm text-muted-foreground">Tasks Completed</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-green-600">7</div>
                <div className="text-sm text-muted-foreground">Day Streak</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-purple-600">8.5</div>
                <div className="text-sm text-muted-foreground">Avg Mood</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-orange-600">156</div>
                <div className="text-sm text-muted-foreground">Focus Hours</div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { action: 'Completed Task', item: 'Write blog post', time: '2 hours ago', reward: 50 },
                  { action: 'Unlocked Achievement', item: 'First Steps', time: '1 day ago', reward: 50 },
                  { action: 'Purchased Reward', item: 'Coffee Break', time: '2 days ago', reward: -75 },
                  { action: 'Maintained Streak', item: '7 days', time: '3 days ago', reward: 100 },
                ].map((activity, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                        <Target className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <div className="font-medium text-foreground">{activity.action}</div>
                        <div className="text-sm text-muted-foreground">{activity.item}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground">{activity.time}</div>
                      <div className={`font-medium ${
                        activity.reward > 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {activity.reward > 0 ? '+' : ''}{activity.reward}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Purchase Modal */}
      <AnimatePresence>
        {showPurchaseModal && selectedItem && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowPurchaseModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-background rounded-2xl shadow-2xl w-full max-w-md p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="text-center space-y-4">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                  <selectedItem.icon className="h-8 w-8 text-primary" />
                </div>
                
                <h3 className="text-xl font-semibold text-foreground">
                  Purchase {selectedItem.name}?
                </h3>
                
                <p className="text-muted-foreground">
                  This will cost you {formatCurrency(selectedItem.cost)} from your balance.
                </p>

                <div className="flex items-center justify-center space-x-2 text-sm text-muted-foreground">
                  <span>Current Balance:</span>
                  <div className="flex items-center space-x-1">
                    <Coins className="h-4 w-4 text-yellow-600" />
                    <span className="font-medium">{formatCurrency(currency)}</span>
                  </div>
                </div>

                <div className="flex space-x-3 pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setShowPurchaseModal(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => handlePurchase(selectedItem)}
                    disabled={currency < selectedItem.cost}
                    className="flex-1"
                  >
                    Confirm Purchase
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
