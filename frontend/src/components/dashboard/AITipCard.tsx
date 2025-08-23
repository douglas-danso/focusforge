import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Brain, RefreshCw, Lightbulb } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

// AI tips database - in real app this would come from backend
const aiTips = [
  {
    id: 1,
    title: 'Perfect Timing',
    tip: 'Your productivity peaks between 10-11 AM. Schedule your most challenging tasks during this window.',
    type: 'timing',
    icon: '⏰',
  },
  {
    id: 2,
    title: 'Mood Boost',
    tip: 'When feeling low energy, try a 5-minute breathing exercise before starting your next task.',
    type: 'mood',
    icon: '🌱',
  },
  {
    id: 3,
    title: 'Focus Flow',
    tip: 'Break large tasks into 25-minute blocks with 5-minute breaks to maintain sustained attention.',
    type: 'focus',
    icon: '🎯',
  },
  {
    id: 4,
    title: 'Environment Matters',
    tip: 'Studies show instrumental music can improve focus by 13%. Try our curated focus playlists.',
    type: 'environment',
    icon: '🎵',
  },
  {
    id: 5,
    title: 'Momentum Building',
    tip: 'Complete 2-3 quick wins before tackling difficult tasks to build psychological momentum.',
    type: 'psychology',
    icon: '🚀',
  },
  {
    id: 6,
    title: 'Recovery Strategy',
    tip: 'After 90 minutes of focused work, take a 15-20 minute break to maintain peak performance.',
    type: 'recovery',
    icon: '🔋',
  },
];

export default function AITipCard() {
  const [currentTip, setCurrentTip] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Rotate tips automatically
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTip((prev) => (prev + 1) % aiTips.length);
    }, 30000); // Change every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setIsRefreshing(true);
    
    setTimeout(() => {
      setCurrentTip((prev) => (prev + 1) % aiTips.length);
      setIsRefreshing(false);
    }, 500);
  };

  const tip = aiTips[currentTip];

  return (
    <Card className="bg-gradient-to-br from-primary/5 via-background to-primary/10 border-primary/20">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-lg">
          <div className="flex items-center space-x-2">
            <Brain className="h-5 w-5 text-primary" />
            <span>AI Insight</span>
          </div>
          
          <Button
            size="icon"
            variant="ghost"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="h-8 w-8"
          >
            <RefreshCw className={`h-4 w-4 transition-transform ${isRefreshing ? 'animate-spin' : ''}`} />
          </Button>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <motion.div
          key={tip.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-3"
        >
          {/* Tip header */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <span className="text-lg">{tip.icon}</span>
            </div>
            
            <div>
              <h4 className="font-medium text-sm text-foreground">
                {tip.title}
              </h4>
              <p className="text-xs text-muted-foreground capitalize">
                {tip.type} tip
              </p>
            </div>
          </div>

          {/* Tip content */}
          <p className="text-sm text-foreground leading-relaxed">
            {tip.tip}
          </p>
        </motion.div>

        {/* Progress indicators */}
        <div className="flex justify-center space-x-2 pt-2">
          {aiTips.map((_, index) => (
            <motion.button
              key={index}
              className={`w-2 h-2 rounded-full transition-colors ${
                index === currentTip ? 'bg-primary' : 'bg-primary/20'
              }`}
              onClick={() => setCurrentTip(index)}
              whileHover={{ scale: 1.2 }}
              whileTap={{ scale: 0.9 }}
            />
          ))}
        </div>

        {/* Action hint */}
        <div className="pt-2 border-t border-border">
          <div className="flex items-center space-x-2 text-primary">
            <Lightbulb className="h-4 w-4" />
            <p className="text-xs font-medium">
              Tip: These insights are personalized based on your productivity patterns
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
