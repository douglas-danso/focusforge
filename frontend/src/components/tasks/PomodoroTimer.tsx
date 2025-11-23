import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Play, Pause, SkipForward, RotateCcw, CheckCircle, Brain, Coffee } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Task, TaskBlock } from '@/types';
import { useTaskStore } from '@/stores/useTaskStore';
import { useUIStore } from '@/stores/useUIStore';
import { formatDuration, formatMinutes } from '@/lib/utils';

interface PomodoroTimerProps {
  task: Task;
  onClose: () => void;
}

type TimerPhase = 'work' | 'break' | 'long_break';

export default function PomodoroTimer({ task, onClose }: PomodoroTimerProps) {
  const [currentPhase, setCurrentPhase] = useState<TimerPhase>('work');
  const [timeRemaining, setTimeRemaining] = useState(25 * 60); // 25 minutes in seconds
  const [isRunning, setIsRunning] = useState(false);
  const [currentBlock, setCurrentBlock] = useState(0);
  const [completedBlocks, setCompletedBlocks] = useState(0);
  const [showBreakModal, setShowBreakModal] = useState(false);
  const [showCompletionModal, setShowCompletionModal] = useState(false);

  const { startTaskBlock, completeTaskBlock } = useTaskStore();
  const { addNotification } = useUIStore();

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const workDuration = 25 * 60; // 25 minutes
  const breakDuration = 5 * 60; // 5 minutes
  const longBreakDuration = 15 * 60; // 15 minutes

  useEffect(() => {
    // Initialize timer with first block
    setTimeRemaining(workDuration);
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (isRunning && timeRemaining > 0) {
      intervalRef.current = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            handlePhaseComplete();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRunning, timeRemaining]);

  const handlePhaseComplete = () => {
    setIsRunning(false);
    
    if (currentPhase === 'work') {
      setCompletedBlocks(prev => prev + 1);
      if (completedBlocks + 1 >= task.estimated_blocks) {
        setShowCompletionModal(true);
      } else {
        setShowBreakModal(true);
      }
    } else {
      // Break completed, start next work session
      setCurrentPhase('work');
      setTimeRemaining(workDuration);
      setCurrentBlock(prev => prev + 1);
    }
  };

  const startWorkSession = async () => {
    try {
      // In a real app, this would call the API to start the block
      await startTaskBlock(task.id, `block-${currentBlock}`);
      setCurrentPhase('work');
      setTimeRemaining(workDuration);
      setIsRunning(true);
      addNotification({ type: 'success', title: 'Work Session Started', message: 'Focus on your task!' });
    } catch (error) {
      addNotification({ type: 'error', title: 'Session Start Failed', message: 'Failed to start work session' });
    }
  };

  const startBreak = (isLongBreak: boolean = false) => {
    setCurrentPhase(isLongBreak ? 'long_break' : 'break');
    setTimeRemaining(isLongBreak ? longBreakDuration : breakDuration);
    setIsRunning(true);
    setShowBreakModal(false);
    
    const message = isLongBreak ? 'Take a longer break!' : 'Time for a short break!';
    addNotification({ type: 'success', title: 'Break Started', message });
  };

  const pauseTimer = () => {
    setIsRunning(false);
  };

  const resumeTimer = () => {
    setIsRunning(true);
  };

  const resetTimer = () => {
    setIsRunning(false);
    setTimeRemaining(workDuration);
    setCurrentPhase('work');
  };

  const skipPhase = () => {
    handlePhaseComplete();
  };

  const completeTask = async () => {
    try {
      // In a real app, this would call the API to complete the task
      await completeTaskBlock(task.id, `block-${currentBlock}`, {});
      addNotification({ type: 'success', title: 'Task Completed!', message: 'Great job finishing your task!' });
      onClose();
    } catch (error) {
      addNotification({ type: 'error', title: 'Completion Failed', message: 'Failed to mark task as complete' });
    }
  };

  const getPhaseInfo = () => {
    switch (currentPhase) {
      case 'work':
        return {
          title: 'Focus Time',
          icon: Brain,
          color: 'text-blue-600',
          bgColor: 'bg-blue-100 dark:bg-blue-900/20',
        };
      case 'break':
        return {
          title: 'Short Break',
          icon: Coffee,
          color: 'text-green-600',
          bgColor: 'bg-green-100 dark:bg-green-900/20',
        };
      case 'long_break':
        return {
          title: 'Long Break',
          icon: Coffee,
          color: 'text-purple-600',
          bgColor: 'bg-purple-100 dark:bg-purple-900/20',
        };
    }
  };

  const phaseInfo = getPhaseInfo();
  const PhaseIcon = phaseInfo.icon;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-background rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-xl ${phaseInfo.bgColor} flex items-center justify-center`}>
              <PhaseIcon className={`h-5 w-5 ${phaseInfo.color}`} />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-foreground">{phaseInfo.title}</h2>
              <p className="text-sm text-muted-foreground">{task.title}</p>
            </div>
          </div>
          <Button
            size="icon"
            variant="ghost"
            onClick={onClose}
            className="h-8 w-8"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="p-6 space-y-6">
          {/* Timer Display */}
          <div className="text-center space-y-4">
            <div className="text-6xl font-bold text-foreground font-mono">
              {formatDuration(timeRemaining)}
            </div>
            
            <div className="flex items-center justify-center space-x-2">
              <span className="text-sm text-muted-foreground">Block</span>
              <span className="font-medium">{currentBlock + 1}</span>
              <span className="text-sm text-muted-foreground">of</span>
              <span className="font-medium">{task.estimated_blocks}</span>
            </div>

            {/* Progress Ring */}
            <div className="relative w-32 h-32 mx-auto">
              <svg className="w-32 h-32 transform -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="transparent"
                  className="text-muted/20"
                />
                <motion.circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="transparent"
                  className={phaseInfo.color}
                  strokeLinecap="round"
                  strokeDasharray={2 * Math.PI * 56}
                  strokeDashoffset={2 * Math.PI * 56 * (1 - (timeRemaining / (currentPhase === 'work' ? workDuration : currentPhase === 'break' ? breakDuration : longBreakDuration)))}
                  transition={{ duration: 1 }}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-2xl font-bold text-foreground">
                    {Math.round(((currentPhase === 'work' ? workDuration : currentPhase === 'break' ? breakDuration : longBreakDuration) - timeRemaining) / (currentPhase === 'work' ? workDuration : currentPhase === 'break' ? breakDuration : longBreakDuration) * 100)}%
                  </div>
                  <div className="text-xs text-muted-foreground">Complete</div>
                </div>
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="flex justify-center space-x-3">
            {!isRunning ? (
              <Button
                onClick={() => currentPhase === 'work' ? startWorkSession() : startBreak(false)}
                size="lg"
                className="px-8"
              >
                <Play className="h-5 w-5 mr-2" />
                Start {currentPhase === 'work' ? 'Work' : 'Break'}
              </Button>
            ) : (
              <Button
                onClick={pauseTimer}
                size="lg"
                variant="outline"
                className="px-8"
              >
                <Pause className="h-5 w-5 mr-2" />
                Pause
              </Button>
            )}

            {!isRunning && timeRemaining < (currentPhase === 'work' ? workDuration : currentPhase === 'break' ? breakDuration : longBreakDuration) && (
              <Button
                onClick={resumeTimer}
                size="lg"
                variant="outline"
                className="px-8"
              >
                <Play className="h-5 w-5 mr-2" />
                Resume
              </Button>
            )}

            <Button
              onClick={skipPhase}
              size="lg"
              variant="outline"
              className="px-8"
            >
              <SkipForward className="h-5 w-5 mr-2" />
              Skip
            </Button>

            <Button
              onClick={resetTimer}
              size="lg"
              variant="ghost"
              className="px-8"
            >
              <RotateCcw className="h-5 w-5 mr-2" />
              Reset
            </Button>
          </div>

          {/* Task Info */}
          <Card>
            <CardContent className="p-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Completed Blocks:</span>
                  <p className="font-medium">{completedBlocks}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Remaining:</span>
                  <p className="font-medium">{task.estimated_blocks - completedBlocks}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Total Time:</span>
                  <p className="font-medium">{formatMinutes(task.duration_minutes)}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Progress:</span>
                  <p className="font-medium">{Math.round((completedBlocks / task.estimated_blocks) * 100)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Break Modal */}
        <AnimatePresence>
          {showBreakModal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/50 flex items-center justify-center"
            >
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                exit={{ scale: 0.9 }}
                className="bg-background rounded-xl p-6 max-w-sm mx-4 text-center"
              >
                <div className="w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  Great work!
                </h3>
                <p className="text-muted-foreground mb-6">
                  You've completed a work block. Time for a break!
                </p>
                <div className="flex space-x-3">
                  <Button
                    onClick={() => startBreak(false)}
                    variant="outline"
                    className="flex-1"
                  >
                    Short Break (5m)
                  </Button>
                  <Button
                    onClick={() => startBreak(true)}
                    className="flex-1"
                  >
                    Long Break (15m)
                  </Button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Completion Modal */}
        <AnimatePresence>
          {showCompletionModal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/50 flex items-center justify-center"
            >
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                exit={{ scale: 0.9 }}
                className="bg-background rounded-xl p-6 max-w-sm mx-4 text-center"
              >
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  Task Complete! 🎉
                </h3>
                <p className="text-muted-foreground mb-6">
                  You've finished all the work blocks for this task.
                </p>
                <div className="flex space-x-3">
                  <Button
                    onClick={onClose}
                    variant="outline"
                    className="flex-1"
                  >
                    Close
                  </Button>
                  <Button
                    onClick={completeTask}
                    className="flex-1"
                  >
                    Mark Complete
                  </Button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
}
