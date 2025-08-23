import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Brain, Clock, Calendar, Tag, Star, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { TaskPriority } from '@/types';
import { useTaskStore } from '@/stores/useTaskStore';
import { useUIStore } from '@/stores/useUIStore';

interface TaskCreateModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export default function TaskCreateModal({ onClose, onSuccess }: TaskCreateModalProps) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    duration_minutes: 25,
    category: '',
    priority: TaskPriority.MEDIUM,
    deadline: '',
    tags: [] as string[],
  });

  const [isLoading, setIsLoading] = useState(false);
  const [showAIPreview, setShowAIPreview] = useState(false);
  const [aiBreakdown, setAiBreakdown] = useState<any>(null);

  const { createTask } = useTaskStore();
  const { addNotification } = useUIStore();

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim()) {
      addNotification({ type: 'error', title: 'Validation Error', message: 'Task title is required' });
      return;
    }

    setIsLoading(true);
    try {
      const result = await createTask({
        title: formData.title,
        description: formData.description,
        duration_minutes: formData.duration_minutes,
        category: formData.category,
        priority: formData.priority,
        deadline: formData.deadline || undefined,
        tags: formData.tags,
      });

      addNotification({ type: 'success', title: 'Task Created', message: 'Task created successfully with AI breakdown!' });
      onSuccess();
    } catch (error: any) {
      addNotification({ type: 'error', title: 'Creation Failed', message: error.message || 'Failed to create task' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAIPreview = async () => {
    if (!formData.title.trim()) {
      addNotification({ type: 'error', title: 'Validation Error', message: 'Please enter a task title first' });
      return;
    }

    setShowAIPreview(true);
    // Simulate AI analysis
    setTimeout(() => {
      setAiBreakdown({
        difficulty_score: 3.5,
        estimated_blocks: Math.ceil(formData.duration_minutes / 25),
        procrastination_risk: 'medium',
        recommended_approach: 'Break this into focused 25-minute sessions with short breaks',
        suggested_ritual_duration: 5,
        breakdown: [
          { title: 'Planning & Setup', estimated_minutes: 10, energy_level: 'medium' },
          { title: 'Core Work', estimated_minutes: formData.duration_minutes - 15, energy_level: 'high' },
          { title: 'Review & Cleanup', estimated_minutes: 5, energy_level: 'low' },
        ],
      });
    }, 1500);
  };

  const priorityOptions = [
    { value: TaskPriority.LOW, label: 'Low', color: 'text-green-600' },
    { value: TaskPriority.MEDIUM, label: 'Medium', color: 'text-yellow-600' },
    { value: TaskPriority.HIGH, label: 'High', color: 'text-orange-600' },
    { value: TaskPriority.URGENT, label: 'Urgent', color: 'text-red-600' },
  ];

  const durationOptions = [15, 25, 45, 60, 90, 120];

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
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <Brain className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-foreground">Create New Task</h2>
              <p className="text-sm text-muted-foreground">AI will help break it down into manageable blocks</p>
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

        <div className="p-6 space-y-6 max-h-[calc(90vh-120px)] overflow-y-auto">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Task Title *
                </label>
                <Input
                  placeholder="What needs to be done?"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  className="text-lg"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Description
                </label>
                <textarea
                  placeholder="Add details about the task..."
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-colors duration-200 resize-none"
                  rows={3}
                />
              </div>
            </div>

            {/* Task Configuration */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Duration
                </label>
                <select
                  value={formData.duration_minutes}
                  onChange={(e) => handleInputChange('duration_minutes', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-colors duration-200"
                >
                  {durationOptions.map(duration => (
                    <option key={duration} value={duration}>
                      {duration} minutes
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Priority
                </label>
                <select
                  value={formData.priority}
                  onChange={(e) => handleInputChange('priority', e.target.value)}
                  className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-colors duration-200"
                >
                  {priorityOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Category
                </label>
                <Input
                  placeholder="e.g., Work, Personal, Study"
                  value={formData.category}
                  onChange={(e) => handleInputChange('category', e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Deadline (Optional)
                </label>
                <Input
                  type="date"
                  value={formData.deadline}
                  onChange={(e) => handleInputChange('deadline', e.target.value)}
                />
              </div>
            </div>

            {/* AI Preview Button */}
            <div className="flex justify-center">
              <Button
                type="button"
                variant="outline"
                onClick={handleAIPreview}
                disabled={!formData.title.trim()}
                className="flex items-center space-x-2"
              >
                <Sparkles className="h-4 w-4" />
                <span>Preview AI Breakdown</span>
              </Button>
            </div>

            {/* AI Breakdown Preview */}
            <AnimatePresence>
              {showAIPreview && aiBreakdown && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-4"
                >
                  <Card className="bg-primary/5 border-primary/20">
                    <CardHeader className="pb-3">
                      <CardTitle className="flex items-center space-x-2 text-lg">
                        <Brain className="h-5 w-5 text-primary" />
                        <span>AI Analysis</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Difficulty:</span>
                          <div className="flex items-center space-x-1 mt-1">
                            {[1, 2, 3, 4, 5].map(star => (
                              <Star
                                key={star}
                                className={`h-4 w-4 ${
                                  star <= aiBreakdown.difficulty_score
                                    ? 'text-yellow-500 fill-current'
                                    : 'text-gray-300'
                                }`}
                              />
                            ))}
                          </div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Estimated Blocks:</span>
                          <p className="font-medium">{aiBreakdown.estimated_blocks}</p>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Risk Level:</span>
                          <p className="font-medium capitalize">{aiBreakdown.procrastination_risk}</p>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Ritual Duration:</span>
                          <p className="font-medium">{aiBreakdown.suggested_ritual_duration}m</p>
                        </div>
                      </div>

                      <div>
                        <p className="text-sm text-muted-foreground mb-2">Recommended Approach:</p>
                        <p className="text-sm text-foreground">{aiBreakdown.recommended_approach}</p>
                      </div>

                      <div>
                        <p className="text-sm text-muted-foreground mb-2">Breakdown:</p>
                        <div className="space-y-2">
                          {aiBreakdown.breakdown.map((block: any, index: number) => (
                            <div key={index} className="flex items-center justify-between p-2 bg-muted rounded-lg">
                              <span className="text-sm font-medium">{block.title}</span>
                              <span className="text-xs text-muted-foreground">{block.estimated_minutes}m</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Submit Button */}
            <div className="flex justify-end space-x-3 pt-4 border-t border-border">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                loading={isLoading}
                disabled={!formData.title.trim()}
              >
                <Sparkles className="h-4 w-4 mr-2" />
                Create Task with AI
              </Button>
            </div>
          </form>
        </div>
      </motion.div>
    </motion.div>
  );
}
