import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Paper,
  IconButton,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Stop,
  Add,
  TrendingUp,
  Assignment,
  Timer,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import api from '../services/api';
import toast from 'react-hot-toast';

function Dashboard() {
  const [stats, setStats] = useState({
    totalTasks: 0,
    completedTasks: 0,
    currentStreak: 0,
    totalSessions: 0,
  });
  const [recentTasks, setRecentTasks] = useState([]);
  const [currentTimer, setCurrentTimer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [tasksResponse, analyticsResponse] = await Promise.all([
        api.get('/tasks'),
        api.get('/analytics'),
      ]);
      
      const tasks = tasksResponse.data;
      const analytics = analyticsResponse.data;
      
      setRecentTasks(tasks.slice(0, 5));
      setStats({
        totalTasks: tasks.length,
        completedTasks: tasks.filter(task => task.status === 'completed').length,
        currentStreak: analytics.current_streak,
        totalSessions: analytics.total_sessions,
      });
    } catch (error) {
      toast.error('Failed to load dashboard data');
      console.error('Dashboard error:', error);
    } finally {
      setLoading(false);
    }
  };

  const startQuickPomodoro = async () => {
    try {
      const response = await api.post('/pomodoro/start', {
        task_id: 'quick_session',
        duration_minutes: 25,
      });
      
      setCurrentTimer(response.data);
      toast.success('Pomodoro session started!');
    } catch (error) {
      toast.error('Failed to start Pomodoro session');
    }
  };

  const StatCard = ({ title, value, icon, color = 'primary' }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ height: '100%', background: `linear-gradient(135deg, ${color === 'primary' ? '#6366f1' : '#ec4899'} 0%, ${color === 'primary' ? '#4f46e5' : '#db2777'} 100%)` }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box>
              <Typography variant="h4" color="white" fontWeight="bold">
                {value}
              </Typography>
              <Typography variant="body2" color="rgba(255,255,255,0.8)">
                {title}
              </Typography>
            </Box>
            <Box sx={{ color: 'white', opacity: 0.8 }}>
              {icon}
            </Box>
          </Box>
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
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Welcome Back! 👋
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Tasks"
            value={stats.totalTasks}
            icon={<Assignment sx={{ fontSize: 40 }} />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Completed"
            value={stats.completedTasks}
            icon={<TrendingUp sx={{ fontSize: 40 }} />}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Current Streak"
            value={stats.currentStreak}
            icon={<Timer sx={{ fontSize: 40 }} />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Sessions"
            value={stats.totalSessions}
            icon={<PlayArrow sx={{ fontSize: 40 }} />}
            color="secondary"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Paper sx={{ p: 3, mb: 3 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6" fontWeight="bold">
                  Quick Actions
                </Typography>
              </Box>
              
              <Box display="flex" gap={2} flexWrap="wrap">
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={startQuickPomodoro}
                  sx={{ borderRadius: 2 }}
                >
                  Start Pomodoro
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Add />}
                  onClick={() => window.location.href = '/tasks'}
                  sx={{ borderRadius: 2 }}
                >
                  Add Task
                </Button>
              </Box>
            </Paper>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" fontWeight="bold" mb={2}>
                Recent Tasks
              </Typography>
              
              {recentTasks.length === 0 ? (
                <Typography color="text.secondary">
                  No tasks yet. Create your first task to get started!
                </Typography>
              ) : (
                <Box>
                  {recentTasks.map((task, index) => (
                    <Box
                      key={task.id}
                      display="flex"
                      alignItems="center"
                      justifyContent="space-between"
                      py={1}
                      borderBottom={index < recentTasks.length - 1 ? '1px solid #333' : 'none'}
                    >
                      <Box>
                        <Typography variant="body1" fontWeight="medium">
                          {task.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {task.status} • {task.duration_minutes} min
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
              )}
            </Paper>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
