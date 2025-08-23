import React from 'react';
import { motion } from 'framer-motion';
import { CheckSquare, Plus, Clock, Star } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

// Placeholder component - will be enhanced with real data
export default function TasksPreview() {
  const mockTasks = [
    {
      id: '1',
      title: 'Complete project proposal',
      difficulty: 4,
      blocks: 3,
      completed: 1,
      urgent: true,
    },
    {
      id: '2', 
      title: 'Review team feedback',
      difficulty: 2,
      blocks: 2,
      completed: 0,
      urgent: false,
    },
    {
      id: '3',
      title: 'Prepare presentation slides',
      difficulty: 3,
      blocks: 4,
      completed: 2,
      urgent: false,
    },
  ];

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <CardTitle className="flex items-center space-x-2 text-lg">
          <CheckSquare className="h-5 w-5 text-primary" />
          <span>Today's Tasks</span>
        </CardTitle>
        
        <Button size="sm" variant="outline">
          <Plus className="h-4 w-4 mr-2" />
          Add Task
        </Button>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {mockTasks.map((task, index) => (
          <motion.div
            key={task.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="p-4 border border-border rounded-xl hover:border-primary/30 transition-colors cursor-pointer"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <h4 className="font-medium text-sm text-foreground truncate">
                    {task.title}
                  </h4>
                  {task.urgent && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400">
                      Urgent
                    </span>
                  )}
                </div>
                
                <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                  <div className="flex items-center space-x-1">
                    <Clock className="h-3 w-3" />
                    <span>{task.blocks} blocks</span>
                  </div>
                  
                  <div className="flex items-center space-x-1">
                    <Star className="h-3 w-3" />
                    <span>{task.difficulty}/5</span>
                  </div>
                  
                  <span>
                    {task.completed}/{task.blocks} done
                  </span>
                </div>
              </div>
              
              {/* Progress circle */}
              <div className="ml-3 flex-shrink-0">
                <div className="w-8 h-8 rounded-full border-2 border-primary/20 flex items-center justify-center relative">
                  <svg className="w-8 h-8 transform -rotate-90 absolute inset-0">
                    <circle
                      cx="16"
                      cy="16"
                      r="14"
                      stroke="currentColor"
                      strokeWidth="2"
                      fill="transparent"
                      className="text-primary"
                      strokeDasharray={`${(task.completed / task.blocks) * 88} 88`}
                    />
                  </svg>
                  <span className="text-xs font-medium text-foreground relative z-10">
                    {Math.round((task.completed / task.blocks) * 100)}%
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
        
        {mockTasks.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <CheckSquare className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm">No tasks for today</p>
            <p className="text-xs">Add a task to get started!</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
