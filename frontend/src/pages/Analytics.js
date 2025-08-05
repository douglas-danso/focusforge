import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  LinearProgress,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';
import { motion } from 'framer-motion';
import api from '../services/api';
import toast from 'react-hot-toast';

const COLORS = ['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#ef4444'];

function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await api.get('/analytics');
      setAnalytics(response.data);
    } catch (error) {
      toast.error('Failed to load analytics');
      console.error('Analytics error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <LinearProgress sx={{ width: '200px' }} />
      </Box>
    );
  }

  if (!analytics) {
    return (
      <Box textAlign="center" py={8}>
        <Typography variant="h6" color="text.secondary">
          No analytics data available
        </Typography>
      </Box>
    );
  }

  const weeklyData = Object.entries(analytics.weekly_stats || {}).map(([date, count]) => ({
    date: new Date(date).toLocaleDateString('en-US', { weekday: 'short' }),
    sessions: count,
  }));

  const moodData = Object.entries(analytics.mood_trends || {}).map(([mood, count]) => ({
    name: mood.charAt(0).toUpperCase() + mood.slice(1),
    value: count,
  }));

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Analytics 📊
      </Typography>

      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card sx={{ background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)' }}>
              <CardContent>
                <Typography variant="h3" color="white" fontWeight="bold">
                  {analytics.total_sessions}
                </Typography>
                <Typography variant="body2" color="rgba(255,255,255,0.8)">
                  Total Sessions
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
          >
            <Card sx={{ background: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)' }}>
              <CardContent>
                <Typography variant="h3" color="white" fontWeight="bold">
                  {analytics.current_streak}
                </Typography>
                <Typography variant="body2" color="rgba(255,255,255,0.8)">
                  Current Streak
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            <Card sx={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
              <CardContent>
                <Typography variant="h3" color="white" fontWeight="bold">
                  {analytics.best_streak}
                </Typography>
                <Typography variant="body2" color="rgba(255,255,255,0.8)">
                  Best Streak
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.3 }}
          >
            <Card sx={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
              <CardContent>
                <Typography variant="h3" color="white" fontWeight="bold">
                  {Math.round((analytics.current_streak / (analytics.best_streak || 1)) * 100)}%
                </Typography>
                <Typography variant="body2" color="rgba(255,255,255,0.8)">
                  Streak Efficiency
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Weekly Activity Chart */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Weekly Activity
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="date" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1e293b', 
                      border: '1px solid #334155',
                      borderRadius: '8px'
                    }} 
                  />
                  <Bar dataKey="sessions" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </motion.div>
        </Grid>

        {/* Mood Distribution */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Mood Distribution
              </Typography>
              {moodData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={moodData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}`}
                    >
                      {moodData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1e293b', 
                        border: '1px solid #334155',
                        borderRadius: '8px'
                      }} 
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Box textAlign="center" py={4}>
                  <Typography color="text.secondary">
                    No mood data available
                  </Typography>
                </Box>
              )}
            </Card>
          </motion.div>
        </Grid>

        {/* Achievements */}
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Achievements 🏆
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center" p={2} border="1px solid #334155" borderRadius={2}>
                    <Typography variant="h4">🔥</Typography>
                    <Typography variant="subtitle2" fontWeight="bold">
                      Streak Master
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {analytics.current_streak >= 7 ? 'Unlocked!' : `${7 - analytics.current_streak} days to go`}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center" p={2} border="1px solid #334155" borderRadius={2}>
                    <Typography variant="h4">💯</Typography>
                    <Typography variant="subtitle2" fontWeight="bold">
                      Century Club
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {analytics.total_sessions >= 100 ? 'Unlocked!' : `${100 - analytics.total_sessions} sessions to go`}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center" p={2} border="1px solid #334155" borderRadius={2}>
                    <Typography variant="h4">🎯</Typography>
                    <Typography variant="subtitle2" fontWeight="bold">
                      Focus Master
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {analytics.best_streak >= 30 ? 'Unlocked!' : `${30 - analytics.best_streak} day streak needed`}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center" p={2} border="1px solid #334155" borderRadius={2}>
                    <Typography variant="h4">🌟</Typography>
                    <Typography variant="subtitle2" fontWeight="bold">
                      Consistency King
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {Object.values(analytics.weekly_stats || {}).every(count => count > 0) && Object.keys(analytics.weekly_stats || {}).length >= 7 ? 'Unlocked!' : 'Complete 7 days in a row'}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Analytics;
