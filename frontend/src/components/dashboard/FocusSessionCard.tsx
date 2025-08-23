import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Clock, Sparkles, Volume2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export default function FocusSessionCard() {
  const [isStarting, setIsStarting] = useState(false);

  const handleStartSession = async () => {
    setIsStarting(true);
    
    // Simulate session start
    setTimeout(() => {
      setIsStarting(false);
      // In real app, this would navigate to focus session or open modal
    }, 1000);
  };

  const upcomingSession = {
    task: 'Complete project proposal',
    duration: 25,
    suggestedRitual: 'Deep Work Preparation',
    playlist: 'Focus Flow Instrumentals',
  };

  return (
    <Card className="bg-gradient-to-br from-blue-50 dark:from-blue-900/10 to-background border-blue-200 dark:border-blue-800/30">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center space-x-2 text-lg">
          <Play className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          <span>Next Focus Session</span>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Session preview */}
        <div className="space-y-3">
          <div className="p-3 bg-white/50 dark:bg-white/5 rounded-xl border border-blue-200/50 dark:border-blue-800/30">
            <h4 className="font-medium text-sm text-foreground mb-2">
              {upcomingSession.task}
            </h4>
            
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="flex items-center space-x-2">
                <Clock className="h-3 w-3 text-muted-foreground" />
                <span className="text-muted-foreground">
                  {upcomingSession.duration} minutes
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                <Sparkles className="h-3 w-3 text-muted-foreground" />
                <span className="text-muted-foreground">
                  With ritual
                </span>
              </div>
            </div>
          </div>

          {/* Session details */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Suggested Ritual:</span>
              <span className="font-medium text-foreground">
                {upcomingSession.suggestedRitual}
              </span>
            </div>
            
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Focus Playlist:</span>
              <div className="flex items-center space-x-1">
                <Volume2 className="h-3 w-3 text-green-500" />
                <span className="font-medium text-foreground">
                  {upcomingSession.playlist}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Session flow preview */}
        <div className="space-y-2">
          <p className="text-xs font-medium text-foreground">Session Flow:</p>
          
          <div className="flex items-center space-x-2 text-xs">
            {[
              { label: 'Ritual', time: '3m', color: 'bg-purple-500' },
              { label: 'Focus', time: '25m', color: 'bg-blue-500' },
              { label: 'Break', time: '5m', color: 'bg-green-500' },
            ].map((step, index) => (
              <React.Fragment key={step.label}>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${step.color}`} />
                  <span className="text-muted-foreground">
                    {step.label} ({step.time})
                  </span>
                </div>
                {index < 2 && (
                  <div className="w-4 h-px bg-border" />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Start button */}
        <motion.div
          className="pt-2"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Button
            onClick={handleStartSession}
            loading={isStarting}
            className="w-full bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700"
            size="lg"
          >
            <Play className="h-4 w-4 mr-2" />
            Start Focus Session
          </Button>
        </motion.div>

        {/* Quick stats */}
        <div className="pt-2 border-t border-border grid grid-cols-2 gap-4 text-center">
          <div>
            <p className="text-lg font-bold text-foreground">4</p>
            <p className="text-xs text-muted-foreground">Sessions today</p>
          </div>
          <div>
            <p className="text-lg font-bold text-foreground">2h 15m</p>
            <p className="text-xs text-muted-foreground">Total focus</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
