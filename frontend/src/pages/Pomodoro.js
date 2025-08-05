import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Stop,
  SkipNext,
  VolumeUp,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import api from '../services/api';
import toast from 'react-hot-toast';

function Pomodoro() {
  const [currentSession, setCurrentSession] = useState(null);
  const [timeLeft, setTimeLeft] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [showTaskSelector, setShowTaskSelector] = useState(false);
  const [sessionHistory, setSessionHistory] = useState([]);

  useEffect(() => {
    fetchTasks();
    fetchSessionHistory();
  }, []);

  useEffect(() => {
    let interval = null;
    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft(timeLeft => timeLeft - 1);
      }, 1000);
    } else if (!isActive && timeLeft !== 0) {
      clearInterval(interval);
    } else if (timeLeft === 0 && currentSession) {
      completeSession();
    }
    return () => clearInterval(interval);
  }, [isActive, timeLeft, currentSession]);

  const fetchTasks = async () => {
    try {
      const response = await api.get('/tasks?status=pending');
      setTasks(response.data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    }
  };

  const fetchSessionHistory = async () => {
    try {
      const response = await api.get('/pomodoro');
      setSessionHistory(response.data.slice(0, 5));
    } catch (error) {
      console.error('Failed to load session history:', error);
    }
  };

  const startSession = async (task) => {
    try {
      const response = await api.post('/pomodoro/start', {
        task_id: task?.id || 'quick_session',
        duration_minutes: task?.duration_minutes || 25,
      });
      
      setCurrentSession(response.data);
      setSelectedTask(task);
      setTimeLeft((task?.duration_minutes || 25) * 60);
      setIsActive(true);
      setShowTaskSelector(false);
      
      toast.success('Pomodoro session started!');
    } catch (error) {
      toast.error('Failed to start session');
      console.error('Start session error:', error);
    }
  };

  const pauseSession = () => {
    setIsActive(false);
    toast.success('Session paused');
  };

  const resumeSession = () => {
    setIsActive(true);
    toast.success('Session resumed');
  };

  const stopSession = () => {
    setIsActive(false);
    setCurrentSession(null);
    setSelectedTask(null);
    setTimeLeft(0);
    toast.success('Session stopped');
  };

  const completeSession = async () => {
    if (!currentSession) return;
    
    try {
      await api.put(`/pomodoro/${currentSession.id}/complete`);
      
      setIsActive(false);
      setCurrentSession(null);
      setSelectedTask(null);
      setTimeLeft(0);
      
      fetchSessionHistory();
      toast.success('🎉 Pomodoro session completed!');
      
      // Add some points for completing a session
      try {
        await api.post('/store/add-currency/25');
      } catch (error) {
        console.error('Failed to add currency:', error);
      }
    } catch (error) {
      toast.error('Failed to complete session');
      console.error('Complete session error:', error);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = () => {
    if (!selectedTask || timeLeft === 0) return 100;
    const totalTime = (selectedTask?.duration_minutes || 25) * 60;
    return ((totalTime - timeLeft) / totalTime) * 100;
  };

  const TimerCircle = () => {
    const radius = 120;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (getProgressPercentage() / 100) * circumference;

    return (
      <Box sx={{ position: 'relative', display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>
        <svg width={280} height={280}>
          <circle
            cx={140}
            cy={140}
            r={radius}
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="8"
            fill="transparent"
          />
          <circle
            cx={140}
            cy={140}
            r={radius}
            stroke="#6366f1"
            strokeWidth="8"
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="timer-circle"
            transform="rotate(-90 140 140)"
          />
        </svg>
        <Box
          sx={{
            position: 'absolute',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography variant="h2" fontWeight="bold" color="primary">
            {formatTime(timeLeft)}
          </Typography>
          {selectedTask && (
            <Typography variant="body1" color="text.secondary" textAlign="center" mt={1}>
              {selectedTask.title}
            </Typography>
          )}
        </Box>
      </Box>
    );
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Pomodoro Timer 🍅
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Card sx={{ p: 4, textAlign: 'center', mb: 3 }}>
              <TimerCircle />
              
              <Box mt={4} display="flex" justifyContent="center" gap={2} flexWrap="wrap">
                {!currentSession ? (
                  <>
                    <Button
                      variant="contained"
                      size="large"
                      startIcon={<PlayArrow />}
                      onClick={() => startSession(null)}
                      sx={{ borderRadius: 2, px: 4 }}
                    >
                      Quick Start (25 min)
                    </Button>
                    <Button
                      variant="outlined"
                      size="large"
                      onClick={() => setShowTaskSelector(true)}
                      sx={{ borderRadius: 2, px: 4 }}
                    >
                      Choose Task
                    </Button>
                  </>
                ) : (
                  <>
                    {isActive ? (
                      <Button
                        variant="contained"
                        size="large"
                        startIcon={<Pause />}
                        onClick={pauseSession}
                        sx={{ borderRadius: 2 }}
                      >
                        Pause
                      </Button>
                    ) : (
                      <Button
                        variant="contained"
                        size="large"
                        startIcon={<PlayArrow />}
                        onClick={resumeSession}
                        sx={{ borderRadius: 2 }}
                      >
                        Resume
                      </Button>
                    )}
                    <Button
                      variant="outlined"
                      size="large"
                      startIcon={<Stop />}
                      onClick={stopSession}
                      sx={{ borderRadius: 2 }}
                    >
                      Stop
                    </Button>
                    <Button
                      variant="outlined"
                      size="large"
                      startIcon={<SkipNext />}
                      onClick={completeSession}
                      sx={{ borderRadius: 2 }}
                    >
                      Complete
                    </Button>
                  </>
                )}
              </Box>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Session Statistics
            </Typography>
            <Box>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body2">Progress</Typography>
                <Typography variant="body2">{Math.round(getProgressPercentage())}%</Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={getProgressPercentage()} 
                sx={{ mb: 2, height: 8, borderRadius: 4 }}
              />
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body2" color="text.secondary">Status</Typography>
                <Chip 
                  label={currentSession ? (isActive ? 'Active' : 'Paused') : 'Idle'} 
                  color={currentSession ? (isActive ? 'success' : 'warning') : 'default'}
                  size="small"
                />
              </Box>
            </Box>
          </Card>

          <Card sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Recent Sessions
            </Typography>
            {sessionHistory.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No sessions completed yet
              </Typography>
            ) : (
              <List dense>
                {sessionHistory.map((session, index) => (
                  <ListItem key={session.id} sx={{ px: 0 }}>
                    <ListItemText
                      primary={`Session ${index + 1}`}
                      secondary={`${session.duration_minutes} min • ${new Date(session.started_at).toLocaleDateString()}`}
                    />
                    <Chip 
                      label={session.is_completed ? 'Completed' : 'Incomplete'} 
                      color={session.is_completed ? 'success' : 'default'}
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Card>
        </Grid>
      </Grid>

      {/* Task Selector Dialog */}
      <Dialog open={showTaskSelector} onClose={() => setShowTaskSelector(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Choose a Task</DialogTitle>
        <DialogContent>
          {tasks.length === 0 ? (
            <Typography color="text.secondary" textAlign="center" py={2}>
              No pending tasks. Create a task first!
            </Typography>
          ) : (
            <List>
              {tasks.map((task) => (
                <ListItem 
                  key={task.id} 
                  button 
                  onClick={() => startSession(task)}
                  sx={{ borderRadius: 2, mb: 1, '&:hover': { bgcolor: 'action.hover' } }}
                >
                  <ListItemText
                    primary={task.title}
                    secondary={`${task.duration_minutes} minutes • ${task.description || 'No description'}`}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
}

export default Pomodoro;
