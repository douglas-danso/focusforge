import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useMoodStore, useMoodActions } from '@/stores/useMoodStore';
import { useNavigate } from 'react-router-dom';

const moodEmojis = ['😔', '😐', '😊', '😄', '🤩'];
const moodLabels = ['Very Sad', 'Neutral', 'Happy', 'Very Happy', 'Ecstatic'];

const moodInfluences = [
  'Good Sleep',
  'Productive Morning',
  'Exercise',
  'Social Time',
  'Achievement',
  'Music',
  'Healthy Food',
  'Nature',
  'Learning',
  'Relaxation'
];

export default function Mood() {
  const navigate = useNavigate();
  const [selectedMood, setSelectedMood] = useState<number | null>(null);
  const [selectedInfluences, setSelectedInfluences] = useState<string[]>([]);
  const [notes, setNotes] = useState('');
  const { moodHistory } = useMoodStore();
  const { logMood, fetchMoodHistory } = useMoodActions();

  useEffect(() => {
    fetchMoodHistory();
  }, [fetchMoodHistory]);

  const toggleInfluence = (influence: string) => {
    setSelectedInfluences((prev) =>
      prev.includes(influence)
        ? prev.filter((i) => i !== influence)
        : [...prev, influence]
    );
  };

  const handleSubmit = async () => {
    if (selectedMood === null) return;

    try {
      await logMood({
        mood: (selectedMood + 1) as any, // Convert 0-4 to 1-5
        energy: 'medium',
        stress: 'low',
        notes: notes,
        activities: selectedInfluences,
      });

      // Reset form
      setSelectedMood(null);
      setSelectedInfluences([]);
      setNotes('');

      // Show success message or navigate
      alert('Mood logged successfully!');
    } catch (error) {
      console.error('Failed to log mood:', error);
      alert('Failed to log mood');
    }
  };

  // Get this week's mood pattern
  const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const thisWeekMoods = weekDays.map((day, idx) => {
    // Mock data - in real app, filter moodHistory by date
    if (idx < 6) {
      return moodEmojis[Math.floor(Math.random() * 4) + 1]; // Random mood for demo
    }
    return '-'; // Today not yet logged
  });

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          How are you feeling?
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Track your mood to optimize productivity
        </p>
      </motion.div>

      {/* Mood Selection */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="p-8">
          <div className="flex justify-center gap-4 mb-8">
            {moodEmojis.map((emoji, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedMood(idx)}
                className={`
                  w-16 h-16 sm:w-20 sm:h-20 rounded-full text-4xl sm:text-5xl
                  flex items-center justify-center transition-all
                  ${
                    selectedMood === idx
                      ? 'bg-primary-500 scale-110 shadow-xl'
                      : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 hover:scale-105'
                  }
                `}
                title={moodLabels[idx]}
              >
                {emoji}
              </button>
            ))}
          </div>
          {selectedMood !== null && (
            <p className="text-center text-lg font-semibold text-gray-900 dark:text-gray-100">
              {moodLabels[selectedMood]}
            </p>
          )}
        </Card>
      </motion.div>

      {/* Influences */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="p-6">
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
            What's influencing your mood?
          </h3>
          <div className="flex flex-wrap gap-2">
            {moodInfluences.map((influence) => (
              <button
                key={influence}
                onClick={() => toggleInfluence(influence)}
                className={`
                  px-4 py-2 rounded-full text-sm font-medium transition-all
                  ${
                    selectedInfluences.includes(influence)
                      ? 'bg-primary-500 text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }
                `}
              >
                {influence}
              </button>
            ))}
          </div>
        </Card>
      </motion.div>

      {/* Notes */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card className="p-6">
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
            Notes (Optional)
          </h3>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Any thoughts to record?"
            className="w-full h-32 p-4 border border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </Card>
      </motion.div>

      {/* Submit Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="flex gap-3"
      >
        <Button
          variant="secondary"
          className="flex-1"
          onClick={() => navigate('/dashboard')}
        >
          Cancel
        </Button>
        <Button
          className="flex-1"
          onClick={handleSubmit}
          disabled={selectedMood === null}
        >
          Save Mood Entry
        </Button>
      </motion.div>

      {/* This Week's Mood Pattern */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Card className="p-6">
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-6">
            This Week's Mood Pattern
          </h3>
          <div className="flex justify-between">
            {weekDays.map((day, idx) => (
              <div key={day} className="text-center">
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                  {day}
                </div>
                <div className="text-3xl">
                  {thisWeekMoods[idx]}
                </div>
              </div>
            ))}
          </div>
        </Card>
      </motion.div>

      {/* Mood History */}
      {moodHistory && moodHistory.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card className="p-6">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
              Recent Entries
            </h3>
            <div className="space-y-3">
              {moodHistory.slice(0, 5).map((entry: any, idx: number) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-xl"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">
                      {moodEmojis[entry.mood - 1] || '😊'}
                    </span>
                    <div>
                      <div className="font-medium text-gray-900 dark:text-gray-100">
                        {moodLabels[entry.mood - 1] || 'Happy'}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(entry.timestamp).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  {entry.notes && (
                    <div className="text-sm text-gray-600 dark:text-gray-400 max-w-xs truncate">
                      {entry.notes}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
