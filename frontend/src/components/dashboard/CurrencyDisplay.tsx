import React from 'react';
import { useUserProfile } from '../../stores/useStoreStore';
import { Card } from '../ui/Card';
import { Coins, TrendingUp, Trophy } from 'lucide-react';

export const CurrencyDisplay: React.FC = () => {
  const userProfile = useUserProfile();

  if (!userProfile) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-yellow-100 rounded-full">
              <Coins className="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Currency Balance</p>
              <p className="text-2xl font-bold text-gray-900">--</p>
            </div>
          </div>
        </div>
      </Card>
    );
  }

  const { currency_balance, total_earned, streak_count } = userProfile;

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-yellow-100 rounded-full">
            <Coins className="w-6 h-6 text-yellow-600" />
          </div>
          <div>
            <p className="text-sm text-gray-600">Currency Balance</p>
            <p className="text-2xl font-bold text-gray-900">
              {currency_balance.toLocaleString()}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="text-center">
            <div className="flex items-center space-x-1 text-green-600">
              <TrendingUp className="w-4 h-4" />
              <span className="text-sm font-medium">{total_earned.toLocaleString()}</span>
            </div>
            <p className="text-xs text-gray-500">Total Earned</p>
          </div>
          
          <div className="text-center">
            <div className="flex items-center space-x-1 text-orange-600">
              <Trophy className="w-4 h-4" />
              <span className="text-sm font-medium">{streak_count}</span>
            </div>
            <p className="text-xs text-gray-500">Day Streak</p>
          </div>
        </div>
      </div>
    </Card>
  );
};
