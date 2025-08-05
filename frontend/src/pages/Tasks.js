import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Chip,
  IconButton,
  MenuItem,
  LinearProgress,
} from '@mui/material';
import {
  Add,
  Delete,
  Edit,
  PlayArrow,
  CheckCircle,
  Schedule,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import toast from 'react-hot-toast';

const taskStatuses = [
  { value: 'pending', label: 'Pending', color: 'default' },
  { value: 'in_progress', label: 'In Progress', color: 'warning' },
  { value: 'completed', label: 'Completed', color: 'success' },
  { value: 'paused', label: 'Paused', color: 'info' },
];

function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    duration_minutes: 25,
    break_minutes: 5,
  });

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await api.get('/tasks');
      setTasks(response.data);
    } catch (error) {
      toast.error('Failed to load tasks');
      console.error('Tasks error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async () => {
    try {
      if (!formData.title.trim()) {
        toast.error('Task title is required');
        return;
      }

      const response = await api.post('/tasks', formData);
      setTasks([response.data, ...tasks]);
      setOpenDialog(false);
      setFormData({
        title: '',
        description: '',
        duration_minutes: 25,
        break_minutes: 5,
      });
      toast.success('Task created successfully!');
    } catch (error) {
      toast.error('Failed to create task');
      console.error('Create task error:', error);
    }
  };

  const handleUpdateTask = async (taskId, updates) => {
    try {
      const response = await api.put(`/tasks/${taskId}`, updates);
      setTasks(tasks.map(task => task.id === taskId ? response.data : task));
      toast.success('Task updated!');
    } catch (error) {
      toast.error('Failed to update task');
      console.error('Update task error:', error);
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      await api.delete(`/tasks/${taskId}`);
      setTasks(tasks.filter(task => task.id !== taskId));
      toast.success('Task deleted!');
    } catch (error) {
      toast.error('Failed to delete task');
      console.error('Delete task error:', error);
    }
  };

  const startPomodoroForTask = async (task) => {
    try {
      const response = await api.post('/pomodoro/start', {
        task_id: task.id,
        duration_minutes: task.duration_minutes,
      });
      
      // Update task status to in_progress
      await handleUpdateTask(task.id, { status: 'in_progress' });
      
      toast.success(`Pomodoro started for "${task.title}"!`);
    } catch (error) {
      toast.error('Failed to start Pomodoro session');
      console.error('Start Pomodoro error:', error);
    }
  };

  const getStatusColor = (status) => {
    const statusConfig = taskStatuses.find(s => s.value === status);
    return statusConfig ? statusConfig.color : 'default';
  };

  const TaskCard = ({ task }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ mb: 2, '&:hover': { transform: 'translateY(-2px)' }, transition: 'transform 0.2s' }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
            <Box flex={1}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                {task.title}
              </Typography>
              {task.description && (
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {task.description}
                </Typography>
              )}
              <Box display="flex" alignItems="center" gap={1} mt={1}>
                <Chip
                  label={taskStatuses.find(s => s.value === task.status)?.label || task.status}
                  color={getStatusColor(task.status)}
                  size="small"
                />
                <Chip
                  icon={<Schedule />}
                  label={`${task.duration_minutes} min`}
                  size="small"
                  variant="outlined"
                />
              </Box>
            </Box>
            <Box display="flex" gap={1}>
              <IconButton
                color="primary"
                onClick={() => startPomodoroForTask(task)}
                disabled={task.status === 'completed'}
              >
                <PlayArrow />
              </IconButton>
              <IconButton
                color="success"
                onClick={() => handleUpdateTask(task.id, { 
                  status: task.status === 'completed' ? 'pending' : 'completed' 
                })}
              >
                <CheckCircle />
              </IconButton>
              <IconButton
                color="error"
                onClick={() => handleDeleteTask(task.id)}
              >
                <Delete />
              </IconButton>
            </Box>
          </Box>
          
          {task.blocks && task.blocks.length > 0 && (
            <Box>
              <Typography variant="subtitle2" fontWeight="bold" mb={1}>
                Task Breakdown:
              </Typography>
              {task.blocks.map((block, index) => (
                <Typography key={index} variant="body2" color="text.secondary">
                  {index + 1}. {block}
                </Typography>
              ))}
            </Box>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <LinearProgress sx={{ width: '200px' }} />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Tasks 📝
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenDialog(true)}
          sx={{ borderRadius: 2 }}
        >
          Add Task
        </Button>
      </Box>

      <AnimatePresence>
        {tasks.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Card sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No tasks yet
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Create your first task to get started with focused work sessions!
              </Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setOpenDialog(true)}
              >
                Create First Task
              </Button>
            </Card>
          </motion.div>
        ) : (
          tasks.map((task) => (
            <TaskCard key={task.id} task={task} />
          ))
        )}
      </AnimatePresence>

      {/* Create/Edit Task Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingTask ? 'Edit Task' : 'Create New Task'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Task Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Duration (minutes)"
                type="number"
                value={formData.duration_minutes}
                onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) || 25 })}
                inputProps={{ min: 1, max: 120 }}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Break (minutes)"
                type="number"
                value={formData.break_minutes}
                onChange={(e) => setFormData({ ...formData, break_minutes: parseInt(e.target.value) || 5 })}
                inputProps={{ min: 1, max: 30 }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateTask} variant="contained">
            {editingTask ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Tasks;
