import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, 
  Filter, 
  Search, 
  Calendar, 
  Clock, 
  Star, 
  CheckCircle,
  Play,
  Pause,
  MoreVertical,
  Edit3,
  Trash2
} from 'lucide-react';
import { useTaskStore } from '@/stores/useTaskStore';
import { useUIStore } from '@/stores/useUIStore';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Task, TaskStatus, TaskPriority } from '@/types';
import { formatDate, formatMinutes, getTaskPriorityColor, getDifficultyStars } from '@/lib/utils';
import TaskCreateModal from '@/components/tasks/TaskCreateModal';
import TaskDetailModal from '@/components/tasks/TaskDetailModal';
import PomodoroTimer from '@/components/tasks/PomodoroTimer';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

type TaskFilter = 'all' | 'today' | 'upcoming' | 'in_progress' | 'completed';

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
  onStart: (task: Task) => void;
}

const TaskCard = ({ task, onEdit, onDelete, onStart }: TaskCardProps) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: task.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.COMPLETED:
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case TaskStatus.IN_PROGRESS:
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400';
      case TaskStatus.PENDING:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  const getPriorityIcon = (priority: TaskPriority) => {
    switch (priority) {
      case TaskPriority.URGENT:
        return '🔴';
      case TaskPriority.HIGH:
        return '🟠';
      case TaskPriority.MEDIUM:
        return '🟡';
      case TaskPriority.LOW:
        return '🟢';
      default:
        return '⚪';
    }
  };

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="cursor-move"
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card className="mb-3 hover:shadow-medium transition-shadow">
        <CardContent className="p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-2">
                <h3 className="font-medium text-foreground truncate">
                  {task.title}
                </h3>
                <span className="text-sm text-muted-foreground">
                  {getPriorityIcon(task.priority)}
                </span>
              </div>
              
              {task.description && (
                <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                  {task.description}
                </p>
              )}

              <div className="flex items-center space-x-4 text-xs text-muted-foreground mb-3">
                <div className="flex items-center space-x-1">
                  <Clock className="h-3 w-3" />
                  <span>{formatMinutes(task.duration_minutes)}</span>
                </div>
                
                <div className="flex items-center space-x-1">
                  <Star className="h-3 w-3" />
                  <span>{getDifficultyStars(task.difficulty_score)}/5</span>
                </div>
                
                <div className="flex items-center space-x-1">
                  <CheckCircle className="h-3 w-3" />
                  <span>{task.blocks_completed}/{task.estimated_blocks} blocks</span>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                  {task.status.replace('_', ' ')}
                </span>
                
                {task.deadline && (
                  <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                    <Calendar className="h-3 w-3" />
                    <span>{formatDate(task.deadline)}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-2 ml-4">
              <Button
                size="sm"
                variant="outline"
                onClick={() => onStart(task)}
                className="h-8 w-8 p-0"
              >
                <Play className="h-4 w-4" />
              </Button>
              
              <div className="relative">
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-8 w-8 p-0"
                >
                  <MoreVertical className="h-4 w-4" />
                </Button>
                
                <div className="absolute right-0 top-full mt-1 w-32 bg-popover border border-border rounded-lg shadow-lg z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => onEdit(task)}
                    className="w-full px-3 py-2 text-left text-sm hover:bg-accent flex items-center space-x-2"
                  >
                    <Edit3 className="h-3 w-3" />
                    <span>Edit</span>
                  </button>
                  <button
                    onClick={() => onDelete(task.id)}
                    className="w-full px-3 py-2 text-left text-sm hover:bg-accent text-red-600 dark:text-red-400 flex items-center space-x-2"
                  >
                    <Trash2 className="h-3 w-3" />
                    <span>Delete</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-3">
            <div className="flex justify-between text-xs text-muted-foreground mb-1">
              <span>Progress</span>
              <span>{Math.round((task.blocks_completed / task.estimated_blocks) * 100)}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <motion.div
                className="bg-primary h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${(task.blocks_completed / task.estimated_blocks) * 100}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default function Tasks() {
  const [selectedFilter, setSelectedFilter] = useState<TaskFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showTimer, setShowTimer] = useState(false);
  const [currentTask, setCurrentTask] = useState<Task | null>(null);

  const { tasks, fetchTasks, isLoading } = useTaskStore();
  const { addNotification } = useUIStore();

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const filteredTasks = tasks.filter(task => {
    const matchesFilter = selectedFilter === 'all' || 
      (selectedFilter === 'today' && task.status === TaskStatus.PENDING) ||
      (selectedFilter === 'upcoming' && task.status === TaskStatus.PENDING) ||
      (selectedFilter === 'in_progress' && task.status === TaskStatus.IN_PROGRESS) ||
      (selectedFilter === 'completed' && task.status === TaskStatus.COMPLETED);
    
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.description?.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesFilter && matchesSearch;
  });

  const handleDragEnd = (event: any) => {
    const { active, over } = event;
    
    if (active.id !== over.id) {
      // In a real app, this would update the backend
      addNotification({ type: 'success', title: 'Task reordered', message: 'Task order updated successfully' });
    }
  };

  const handleCreateTask = () => {
    setShowCreateModal(true);
  };

  const handleEditTask = (task: Task) => {
    setSelectedTask(task);
    setShowDetailModal(true);
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      // In a real app, this would call the API
      addNotification({ type: 'success', title: 'Task deleted', message: 'Task removed successfully' });
    } catch (error) {
      addNotification({ type: 'error', title: 'Delete failed', message: 'Failed to delete task' });
    }
  };

  const handleStartTask = (task: Task) => {
    setCurrentTask(task);
    setShowTimer(true);
  };

  const filters: { key: TaskFilter; label: string; count: number }[] = [
    { key: 'all', label: 'All', count: tasks.length },
    { key: 'today', label: 'Today', count: tasks.filter(t => t.status === TaskStatus.PENDING).length },
    { key: 'upcoming', label: 'Upcoming', count: tasks.filter(t => t.status === TaskStatus.PENDING).length },
    { key: 'in_progress', label: 'In Progress', count: tasks.filter(t => t.status === TaskStatus.IN_PROGRESS).length },
    { key: 'completed', label: 'Completed', count: tasks.filter(t => t.status === TaskStatus.COMPLETED).length },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Tasks</h1>
          <p className="text-muted-foreground mt-1">
            Manage your tasks with AI-powered breakdowns and Pomodoro timers
          </p>
        </div>

        <Button onClick={handleCreateTask} size="lg">
          <Plus className="h-5 w-5 mr-2" />
          Add Task
        </Button>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <div className="flex bg-muted rounded-lg p-1">
            {filters.map((filter) => (
              <button
                key={filter.key}
                onClick={() => setSelectedFilter(filter.key)}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  selectedFilter === filter.key
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {filter.label}
                <span className="ml-1 text-xs opacity-70">({filter.count})</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Task List */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-muted-foreground">Loading tasks...</p>
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium text-foreground mb-2">
              {searchQuery ? 'No tasks found' : 'No tasks yet'}
            </h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery ? 'Try adjusting your search terms' : 'Create your first task to get started'}
            </p>
            {!searchQuery && (
              <Button onClick={handleCreateTask}>
                <Plus className="h-4 w-4 mr-2" />
                Create Task
              </Button>
            )}
          </div>
        ) : (
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
          >
            <SortableContext
              items={filteredTasks.map(task => task.id)}
              strategy={verticalListSortingStrategy}
            >
              <AnimatePresence>
                {filteredTasks.map(task => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onEdit={handleEditTask}
                    onDelete={handleDeleteTask}
                    onStart={handleStartTask}
                  />
                ))}
              </AnimatePresence>
            </SortableContext>
          </DndContext>
        )}
      </div>

      {/* Modals */}
      <AnimatePresence>
        {showCreateModal && (
          <TaskCreateModal
            onClose={() => setShowCreateModal(false)}
            onSuccess={() => {
              setShowCreateModal(false);
              fetchTasks();
            }}
          />
        )}

        {showDetailModal && selectedTask && (
          <TaskDetailModal
            task={selectedTask}
            onClose={() => {
              setShowDetailModal(false);
              setSelectedTask(null);
            }}
            onUpdate={() => {
              setShowDetailModal(false);
              setSelectedTask(null);
              fetchTasks();
            }}
          />
        )}

        {showTimer && currentTask && (
          <PomodoroTimer
            task={currentTask}
            onClose={() => {
              setShowTimer(false);
              setCurrentTask(null);
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
