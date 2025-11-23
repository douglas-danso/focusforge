import React from 'react';
import { motion } from 'framer-motion';
import { Target } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

interface ProgressRingProps {
  completed: number;
  total: number;
  size?: number;
  strokeWidth?: number;
}

export default function ProgressRing({ 
  completed, 
  total, 
  size = 120, 
  strokeWidth = 8 
}: ProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const percentage = total > 0 ? (completed / total) * 100 : 0;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const getColor = () => {
    if (percentage >= 100) return '#10b981'; // Green
    if (percentage >= 75) return '#0066FF'; // Primary blue
    if (percentage >= 50) return '#f59e0b'; // Amber
    return '#e5e7eb'; // Gray
  };

  const getMessage = () => {
    if (percentage >= 100) return 'Amazing! All done! 🎉';
    if (percentage >= 75) return 'Almost there! 💪';
    if (percentage >= 50) return 'Great progress! 🚀';
    if (percentage > 0) return 'Getting started! ⭐';
    return 'Ready to begin? 📋';
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center space-x-2 text-lg">
          <Target className="h-5 w-5 text-primary" />
          <span>Daily Progress</span>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="flex flex-col items-center space-y-4">
        {/* Progress ring */}
        <div className="relative">
          <svg width={size} height={size} className="transform -rotate-90">
            {/* Background circle */}
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              stroke="currentColor"
              strokeWidth={strokeWidth}
              fill="transparent"
              className="text-muted/20"
            />
            
            {/* Progress circle */}
            <motion.circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              stroke={getColor()}
              strokeWidth={strokeWidth}
              fill="transparent"
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{ duration: 1.5, ease: 'easeOut' }}
            />
          </svg>
          
          {/* Center content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <motion.span
              key={percentage}
              initial={{ scale: 1.2, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
              className="text-2xl font-bold text-foreground"
            >
              {Math.round(percentage)}%
            </motion.span>
            <span className="text-xs text-muted-foreground">complete</span>
          </div>
        </div>

        {/* Stats */}
        <div className="text-center space-y-1">
          <p className="text-sm text-muted-foreground">
            {completed} of {total} tasks completed
          </p>
          <motion.p
            key={getMessage()}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-xs font-medium text-foreground"
          >
            {getMessage()}
          </motion.p>
        </div>

        {/* Quick stats */}
        <div className="w-full pt-2 border-t border-border">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <p className="text-lg font-bold text-foreground">{completed}</p>
              <p className="text-xs text-muted-foreground">Done</p>
            </div>
            <div>
              <p className="text-lg font-bold text-foreground">{Math.max(0, total - completed)}</p>
              <p className="text-xs text-muted-foreground">Remaining</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
