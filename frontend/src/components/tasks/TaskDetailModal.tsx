import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Edit3, Save, Clock, Star, Calendar, Tag, Brain, CheckCircle, Play } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Task, TaskPriority, TaskStatus } from '@/types';
import { formatDate, formatMinutes, getDifficultyStars } from '@/lib/utils';
import { useTaskStore } from '@/stores/useTaskStore';
import { useUIStore } from '@/stores/useUIStore';

interface TaskDetailModalProps {
  task: Task;
  onClose: () => void;
  onUpdate: () => void;
}

export default function TaskDetailModal({ task, onClose, onUpdate }: TaskDetailModalProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTask, setEditedTask] = useState<Task>(task);
  const [isLoading, setIsLoading] = useState(false);

  const { updateTaskAPI } = useTaskStore();
  const { addNotification } = useUIStore();

  const handleInputChange = (field: string, value: any) => {
    setEditedTask(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      await updateTaskAPI(task.id, editedTask);
      addNotification({ type: 'success', title: 'Task Updated', message: 'Task details saved successfully' });
      setIsEditing(false);
      onUpdate();
    } catch (error: any) {
      addNotification({ type: 'error', title: 'Update Failed', message: error.message || 'Failed to update task' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setEditedTask(task);
    setIsEditing(false);
  };

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case TaskPriority.URGENT:
        return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/20';
      case TaskPriority.HIGH:
        return 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/20';
      case TaskPriority.MEDIUM:
        return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20';
      case TaskPriority.LOW:
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20';
      default:
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20';
    }
  };

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.COMPLETED:
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20';
      case TaskStatus.IN_PROGRESS:
        return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20';
      case TaskStatus.PENDING:
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20';
      default:
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20';
    }
  };

  const priorityOptions = [
    { value: TaskPriority.LOW, label: 'Low' },
    { value: TaskPriority.MEDIUM, label: 'Medium' },
    { value: TaskPriority.HIGH, label: 'High' },
    { value: TaskPriority.URGENT, label: 'Urgent' },
  ];

  const statusOptions = [
    { value: TaskStatus.PENDING, label: 'Pending' },
    { value: TaskStatus.IN_PROGRESS, label: 'In Progress' },
    { value: TaskStatus.COMPLETED, label: 'Completed' },
  ];

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
        className="bg-background rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <Brain className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-foreground">Task Details</h2>
              <p className="text-sm text-muted-foreground">View and edit task information</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {!isEditing ? (
              <Button
                onClick={() => setIsEditing(true)}
                variant="outline"
                size="sm"
              >
                <Edit3 className="h-4 w-4 mr-2" />
                Edit
              </Button>
            ) : (
              <>
                <Button
                  onClick={handleCancel}
                  variant="outline"
                  size="sm"
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleSave}
                  loading={isLoading}
                  size="sm"
                >
                  <Save className="h-4 w-4 mr-2" />
                  Save
                </Button>
              </>
            )}
            <Button
              size="icon"
              variant="ghost"
              onClick={onClose}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="p-6 space-y-6 max-h-[calc(90vh-120px)] overflow-y-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column - Basic Info */}
            <div className="space-y-6">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Task Title
                </label>
                {isEditing ? (
                  <Input
                    value={editedTask.title}
                    onChange={(e) => handleInputChange('title', e.target.value)}
                    className="text-lg"
                  />
                ) : (
                  <h3 className="text-xl font-semibold text-foreground">{task.title}</h3>
                )}
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Description
                </label>
                {isEditing ? (
                  <textarea
                    value={editedTask.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-colors duration-200 resize-none"
                    rows={4}
                  />
                ) : (
                  <p className="text-muted-foreground">
                    {task.description || 'No description provided'}
                  </p>
                )}
              </div>

              {/* Status and Priority */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Status
                  </label>
                  {isEditing ? (
                    <select
                      value={editedTask.status}
                      onChange={(e) => handleInputChange('status', e.target.value)}
                      className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-colors duration-200"
                    >
                      {statusOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(task.status)}`}>
                      {task.status.replace('_', ' ')}
                    </span>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Priority
                  </label>
                  {isEditing ? (
                    <select
                      value={editedTask.priority}
                      onChange={(e) => handleInputChange('priority', e.target.value)}
                      className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-colors duration-200"
                    >
                      {priorityOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(task.priority)}`}>
                      {task.priority}
                    </span>
                  )}
                </div>
              </div>

              {/* Category and Tags */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Category
                  </label>
                  {isEditing ? (
                    <Input
                      value={editedTask.category}
                      onChange={(e) => handleInputChange('category', e.target.value)}
                      placeholder="e.g., Work, Personal"
                    />
                  ) : (
                    <p className="text-foreground">{task.category || 'Uncategorized'}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Tags
                  </label>
                  {isEditing ? (
                    <Input
                      value={editedTask.tags.join(', ')}
                      onChange={(e) => handleInputChange('tags', e.target.value.split(',').map(tag => tag.trim()))}
                      placeholder="tag1, tag2, tag3"
                    />
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {task.tags.length > 0 ? (
                        task.tags.map((tag, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-muted text-muted-foreground rounded-md text-xs"
                          >
                            {tag}
                          </span>
                        ))
                      ) : (
                        <span className="text-muted-foreground">No tags</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Right Column - Stats and Actions */}
            <div className="space-y-6">
              {/* Quick Stats */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">Task Statistics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-3 bg-muted rounded-lg">
                      <div className="text-2xl font-bold text-primary">{task.estimated_blocks}</div>
                      <div className="text-xs text-muted-foreground">Total Blocks</div>
                    </div>
                    <div className="text-center p-3 bg-muted rounded-lg">
                      <div className="text-2xl font-bold text-green-600">{task.blocks_completed}</div>
                      <div className="text-xs text-muted-foreground">Completed</div>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Duration:</span>
                      <span className="font-medium">{formatMinutes(task.duration_minutes)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Difficulty:</span>
                      <div className="flex items-center space-x-1">
                        {[1, 2, 3, 4, 5].map(star => (
                          <Star
                            key={star}
                            className={`h-4 w-4 ${
                              star <= getDifficultyStars(task.difficulty_score)
                                ? 'text-yellow-500 fill-current'
                                : 'text-gray-300'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Progress:</span>
                      <span className="font-medium">
                        {Math.round((task.blocks_completed / task.estimated_blocks) * 100)}%
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* AI Insights */}
              {task.agent_guidance && (
                <Card className="bg-primary/5 border-primary/20">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center space-x-2 text-lg">
                      <Brain className="h-5 w-5 text-primary" />
                      <span>AI Insights</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Recommended Approach:</p>
                      <p className="text-sm text-foreground">{task.recommended_approach || 'No specific approach recommended'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Motivation:</p>
                      <p className="text-sm text-foreground">{task.agent_guidance?.motivation || 'Stay focused and make progress!'}</p>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Actions */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button className="w-full" size="lg">
                    <Play className="h-4 w-4 mr-2" />
                    Start Focus Session
                  </Button>
                  <Button variant="outline" className="w-full" size="lg">
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Mark Complete
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Bottom Actions */}
          {!isEditing && (
            <div className="flex justify-center pt-4 border-t border-border">
              <Button onClick={onClose} variant="outline">
                Close
              </Button>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
