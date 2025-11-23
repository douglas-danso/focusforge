import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useNavigate, useLocation } from 'react-router-dom';
import { orchestratorAPI } from '../services/api';

interface FocusRitual {
  type: string;
  description: string;
  icon: string;
}

interface FocusSessionData {
  task_id?: string;
  task_title?: string;
  duration_minutes?: number;
  rituals?: FocusRitual[];
  subtasks?: any[];
  session_id?: string;
}

export default function FocusSession() {
  const navigate = useNavigate();
  const location = useLocation();
  const [time, setTime] = useState(25 * 60); // 25 minutes in seconds
  const [isRunning, setIsRunning] = useState(false);
  const [session, setSession] = useState(1);
  const [totalSessions, setTotalSessions] = useState(4);
  const [sessionData, setSessionData] = useState<FocusSessionData | null>(null);
  const [aiRituals, setAiRituals] = useState<FocusRitual[]>([]);
  const [isLoadingRituals, setIsLoadingRituals] = useState(true);

  useEffect(() => {
    // Load AI focus session data
    loadFocusSession();
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning && time > 0) {
      interval = setInterval(() => {
        setTime((prevTime) => prevTime - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRunning, time]);

  const loadFocusSession = async () => {
    setIsLoadingRituals(true);
    try {
      // Get task info from navigation state if available
      const taskData = (location.state as any)?.task;

      // Start AI-enhanced focus session
      const response = await orchestratorAPI.startFocusSession({
        task_id: taskData?.id,
        duration_minutes: 25,
        session_type: 'pomodoro',
      });

      if (response.data) {
        setSessionData(response.data);

        // Set AI-generated rituals
        if (response.data.rituals && response.data.rituals.length > 0) {
          setAiRituals(response.data.rituals);
        } else {
          // Fallback rituals
          setAiRituals([
            { type: 'music', description: 'Focus music suggested for this session', icon: '🎵' },
            { type: 'hydration', description: 'Keep water nearby - stay hydrated', icon: '💧' },
            { type: 'goal', description: 'Focus on completing one subtask at a time', icon: '🎯' },
          ]);
        }

        // Set duration if provided
        if (response.data.duration_minutes) {
          setTime(response.data.duration_minutes * 60);
        }
      }
    } catch (error) {
      console.error('Failed to load AI focus session:', error);
      // Set default rituals on error
      setAiRituals([
        { type: 'focus', description: 'Eliminate distractions for maximum focus', icon: '🧘' },
        { type: 'timer', description: 'Work in focused 25-minute intervals', icon: '⏱️' },
        { type: 'breaks', description: 'Take short breaks between sessions', icon: '☕' },
      ]);
    } finally {
      setIsLoadingRituals(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handlePlayPause = () => {
    setIsRunning(!isRunning);
  };

  const handleStop = () => {
    setIsRunning(false);
    setTime(25 * 60);
  };

  const handleSkip = () => {
    if (session < totalSessions) {
      setSession(session + 1);
      setTime(25 * 60);
      setIsRunning(false);
    }
  };

  const subtasks = [
    { id: 1, title: 'Set up JWT token generation and validation', completed: true },
    { id: 2, title: 'Create user registration endpoint', completed: true },
    { id: 3, title: 'Implement login/logout functionality', completed: false },
    { id: 4, title: 'Add refresh token rotation', completed: false },
    { id: 5, title: 'Set up password reset flow', completed: false },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Focus Session
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Stay focused, work smart
        </p>
      </motion.div>

      {/* Timer Widget */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="p-12 gradient-purple text-white text-center overflow-hidden relative">
          <div className="relative z-10">
            <div className="text-8xl lg:text-9xl font-bold mb-6 font-mono tracking-tight">
              {formatTime(time)}
            </div>
            <h2 className="text-2xl font-semibold mb-8 opacity-95">
              {sessionData?.task_title || 'Ready to focus?'}
            </h2>

            <div className="flex gap-6 justify-center mb-8">
              <button
                onClick={handlePlayPause}
                className="w-20 h-20 rounded-full bg-white/20 backdrop-blur-sm border-3 border-white hover:bg-white/30 transition-all text-3xl flex items-center justify-center"
              >
                {isRunning ? '⏸️' : '▶️'}
              </button>
              <button
                onClick={handleStop}
                className="w-24 h-24 rounded-full bg-white text-purple-600 hover:bg-white/90 transition-all text-4xl flex items-center justify-center shadow-xl"
              >
                ⏹️
              </button>
              <button
                onClick={handleSkip}
                className="w-20 h-20 rounded-full bg-white/20 backdrop-blur-sm border-3 border-white hover:bg-white/30 transition-all text-3xl flex items-center justify-center"
              >
                ⏭️
              </button>
            </div>

            <div className="flex gap-12 justify-center text-lg">
              <div>
                <div className="opacity-80 mb-1">Session</div>
                <div className="text-2xl font-semibold">{session} of {totalSessions}</div>
              </div>
              <div>
                <div className="opacity-80 mb-1">Total Time</div>
                <div className="text-2xl font-semibold">50:25</div>
              </div>
              <div>
                <div className="opacity-80 mb-1">Points</div>
                <div className="text-2xl font-semibold">+25</div>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* AI Focus Rituals */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-3xl">🤖</span>
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              AI Focus Rituals
            </h3>
          </div>
          <div className="space-y-3">
            {isLoadingRituals ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-xl animate-pulse">
                    <div className="w-8 h-8 bg-gray-300 dark:bg-gray-700 rounded"></div>
                    <div className="flex-1">
                      <div className="h-5 bg-gray-300 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
                      <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-full"></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              aiRituals.map((ritual, idx) => (
                <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-xl">
                  <span className="text-2xl">{ritual.icon}</span>
                  <div>
                    <div className="font-semibold text-gray-900 dark:text-gray-100 capitalize">
                      {ritual.type} Ritual
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {ritual.description}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      </motion.div>

      {/* Current Subtasks */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              Current Subtasks
            </h3>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              2 of 5 completed
            </span>
          </div>
          <div className="space-y-2">
            {subtasks.map((subtask) => (
              <label
                key={subtask.id}
                className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-colors ${
                  subtask.completed
                    ? 'bg-gray-50 dark:bg-gray-800'
                    : 'bg-blue-50 dark:bg-blue-900/20'
                }`}
              >
                <input
                  type="checkbox"
                  checked={subtask.completed}
                  className="w-5 h-5 rounded"
                  readOnly
                />
                <span
                  className={`flex-1 ${
                    subtask.completed
                      ? 'text-gray-500 dark:text-gray-400 line-through'
                      : 'text-gray-900 dark:text-gray-100 font-semibold'
                  }`}
                >
                  {subtask.title}
                </span>
              </label>
            ))}
          </div>
        </Card>
      </motion.div>

      {/* Actions */}
      <div className="flex gap-3 justify-center">
        <Button variant="secondary" onClick={() => navigate('/dashboard')}>
          Back to Dashboard
        </Button>
        <Button onClick={() => navigate('/tasks')}>
          View All Tasks
        </Button>
      </div>
    </div>
  );
}
