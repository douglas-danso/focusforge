import React, { useState } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { useMoodComputed, useMoodActions } from '../../stores/useMoodStore';
import { useUIActions } from '../../stores/useUIStore';
import { getMoodEmoji, getMoodColor } from '../../lib/utils';

export const MoodCheckCard: React.FC = () => {
  const [selectedMood, setSelectedMood] = useState<number>(5);
  const [isLogging, setIsLogging] = useState(false);
  
  const { getAverageMood, getMoodTrend } = useMoodComputed();
  const { logMood } = useMoodActions();
  const { addNotification } = useUIActions();

  const averageMood = getAverageMood(7);
  const moodTrend = getMoodTrend();

  const handleMoodLog = async () => {
    setIsLogging(true);
    
    try {
      await logMood({
        mood_score: selectedMood,
        energy_level: 5,
        stress_level: 5,
        notes: 'Quick mood check from dashboard',
      });
      
      addNotification({
        type: 'success',
        title: 'Mood Logged',
        message: 'Your mood has been recorded successfully!',
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to log mood. Please try again.',
      });
    } finally {
      setIsLogging(false);
    }
  };

  const getTrendIcon = () => {
    switch (moodTrend) {
      case 'improving':
        return '📈';
      case 'declining':
        return '📉';
      default:
        return '➡️';
    }
  };

  const getTrendColor = () => {
    switch (moodTrend) {
      case 'improving':
        return 'text-green-600';
      case 'declining':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">How are you feeling?</h3>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">7-day avg:</span>
          <span className={`font-medium ${getMoodColor(averageMood)}`}>
            {averageMood.toFixed(1)}/10
          </span>
          <span className={`text-lg ${getTrendColor()}`}>{getTrendIcon()}</span>
        </div>
      </div>

      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Rate your mood:</span>
          <span className="text-sm font-medium text-gray-900">
            {selectedMood}/10 {getMoodEmoji(selectedMood)}
          </span>
        </div>
        
        <div className="flex items-center space-x-1">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((mood) => (
            <button
              key={mood}
              onClick={() => setSelectedMood(mood)}
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                selectedMood === mood
                  ? `${getMoodColor(mood)} bg-opacity-20 border-2 border-current`
                  : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
              }`}
            >
              {mood}
            </button>
          ))}
        </div>
      </div>

      <Button
        onClick={handleMoodLog}
        disabled={isLogging}
        className="w-full"
        variant="default"
      >
        {isLogging ? 'Logging...' : 'Log Mood'}
      </Button>

      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          Quick mood logging helps track your daily well-being
        </p>
      </div>
    </Card>
  );
};
