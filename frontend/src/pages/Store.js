import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  ShoppingCart,
  AttachMoney,
  Coffee,
  SportsEsports,
  Hotel,
  MusicNote,
  FastFood,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import api from '../services/api';
import toast from 'react-hot-toast';

const itemIcons = {
  break: <Coffee />,
  entertainment: <SportsEsports />,
  rest: <Hotel />,
  music: <MusicNote />,
  food: <FastFood />,
};

function Store() {
  const [items, setItems] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [purchaseDialog, setPurchaseDialog] = useState({ open: false, item: null });

  useEffect(() => {
    fetchStoreData();
  }, []);

  const fetchStoreData = async () => {
    try {
      setLoading(true);
      const [itemsResponse, profileResponse] = await Promise.all([
        api.get('/store/items'),
        api.get('/store/profile'),
      ]);
      
      setItems(itemsResponse.data);
      setProfile(profileResponse.data);
    } catch (error) {
      toast.error('Failed to load store data');
      console.error('Store error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (item) => {
    try {
      const response = await api.post(`/store/purchase/${item.name}`);
      toast.success(response.data.message);
      
      // Refresh profile to update currency
      const profileResponse = await api.get('/store/profile');
      setProfile(profileResponse.data);
      
      setPurchaseDialog({ open: false, item: null });
    } catch (error) {
      const message = error.response?.data?.detail || 'Purchase failed';
      toast.error(message);
    }
  };

  const openPurchaseDialog = (item) => {
    setPurchaseDialog({ open: true, item });
  };

  const closePurchaseDialog = () => {
    setPurchaseDialog({ open: false, item: null });
  };

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
          Reward Store 🏪
        </Typography>
        
        <Card sx={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
          <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 2 }}>
            <AttachMoney sx={{ color: 'white' }} />
            <Typography variant="h6" color="white" fontWeight="bold">
              {profile?.currency || 0} Points
            </Typography>
          </CardContent>
        </Card>
      </Box>

      <Typography variant="body1" color="text.secondary" mb={4}>
        Earn points by completing Pomodoro sessions and redeem them for rewards!
      </Typography>

      <Grid container spacing={3}>
        {items.map((item, index) => (
          <Grid item xs={12} sm={6} md={4} key={item.name}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Card 
                sx={{ 
                  height: '100%',
                  '&:hover': { transform: 'translateY(-4px)', boxShadow: 6 },
                  transition: 'all 0.3s ease',
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Box 
                      sx={{ 
                        p: 2, 
                        borderRadius: 2, 
                        backgroundColor: 'primary.main',
                        color: 'white',
                        mr: 2 
                      }}
                    >
                      {itemIcons[item.type] || <ShoppingCart />}
                    </Box>
                    <Box>
                      <Typography variant="h6" fontWeight="bold">
                        {item.name}
                      </Typography>
                      <Chip 
                        label={item.type} 
                        size="small" 
                        color="primary" 
                        variant="outlined" 
                      />
                    </Box>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" mb={3}>
                    {item.description || 'A reward for your hard work!'}
                  </Typography>
                  
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="h6" fontWeight="bold" color="primary">
                      {item.cost} Points
                    </Typography>
                    
                    <Button
                      variant="contained"
                      size="small"
                      onClick={() => openPurchaseDialog(item)}
                      disabled={(profile?.currency || 0) < item.cost}
                      sx={{ borderRadius: 2 }}
                    >
                      {(profile?.currency || 0) < item.cost ? 'Need More Points' : 'Purchase'}
                    </Button>
                  </Box>
                  
                  {profile?.purchases?.includes(item.name) && (
                    <Chip 
                      label="✓ Purchased" 
                      color="success" 
                      size="small" 
                      sx={{ mt: 2, width: '100%' }}
                    />
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      {/* How to Earn Points */}
      <Card sx={{ mt: 4, p: 3, background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)' }}>
        <Typography variant="h6" color="white" fontWeight="bold" gutterBottom>
          How to Earn Points 💡
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" sx={{ mb: 1 }}>🍅</Typography>
              <Typography variant="body2" color="rgba(255,255,255,0.9)">
                Complete a Pomodoro
              </Typography>
              <Typography variant="body2" color="rgba(255,255,255,0.7)">
                +25 points
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" sx={{ mb: 1 }}>✅</Typography>
              <Typography variant="body2" color="rgba(255,255,255,0.9)">
                Complete a Task
              </Typography>
              <Typography variant="body2" color="rgba(255,255,255,0.7)">
                +50 points
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" sx={{ mb: 1 }}>🔥</Typography>
              <Typography variant="body2" color="rgba(255,255,255,0.9)">
                Daily Streak
              </Typography>
              <Typography variant="body2" color="rgba(255,255,255,0.7)">
                +10 points/day
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" sx={{ mb: 1 }}>🎯</Typography>
              <Typography variant="body2" color="rgba(255,255,255,0.9)">
                Weekly Goal
              </Typography>
              <Typography variant="body2" color="rgba(255,255,255,0.7)">
                +100 points
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Card>

      {/* Purchase Confirmation Dialog */}
      <Dialog 
        open={purchaseDialog.open} 
        onClose={closePurchaseDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Confirm Purchase
        </DialogTitle>
        <DialogContent>
          {purchaseDialog.item && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {purchaseDialog.item.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {purchaseDialog.item.description || 'A reward for your hard work!'}
              </Typography>
              <Box mt={2} p={2} bgcolor="background.paper" borderRadius={2}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Cost:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {purchaseDialog.item.cost} points
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Current Balance:</Typography>
                  <Typography variant="body2">
                    {profile?.currency || 0} points
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" fontWeight="bold">After Purchase:</Typography>
                  <Typography variant="body2" fontWeight="bold" color="primary">
                    {(profile?.currency || 0) - purchaseDialog.item.cost} points
                  </Typography>
                </Box>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closePurchaseDialog}>
            Cancel
          </Button>
          <Button 
            onClick={() => handlePurchase(purchaseDialog.item)} 
            variant="contained"
            disabled={(profile?.currency || 0) < (purchaseDialog.item?.cost || 0)}
          >
            Confirm Purchase
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Store;
