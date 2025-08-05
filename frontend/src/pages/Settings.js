import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Switch,
  FormControlLabel,
  Divider,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem,
} from '@mui/material';
import {
  Notifications,
  Palette,
  VolumeUp,
  Timer,
  Language,
  Security,
  CloudSync,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

function Settings() {
  const [settings, setSettings] = useState({
    notifications: true,
    sound: true,
    darkMode: true,
    autoBreak: true,
    pomodoroLength: 25,
    shortBreakLength: 5,
    longBreakLength: 15,
    language: 'en',
    theme: 'dark',
  });

  const [spotifyDialog, setSpotifyDialog] = useState(false);
  const [spotifyConfig, setSpotifyConfig] = useState({
    clientId: '',
    clientSecret: '',
  });

  const handleSettingChange = (key, value) => {
    setSettings({ ...settings, [key]: value });
    toast.success('Setting updated!');
  };

  const saveSpotifyConfig = () => {
    // In a real app, this would save to backend
    localStorage.setItem('spotifyConfig', JSON.stringify(spotifyConfig));
    setSpotifyDialog(false);
    toast.success('Spotify configuration saved!');
  };

  const exportData = () => {
    // In a real app, this would export user data
    toast.success('Data export started! Check your downloads.');
  };

  const importData = () => {
    // In a real app, this would import user data
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        toast.success('Data imported successfully!');
      }
    };
    input.click();
  };

  const SettingCard = ({ title, icon, children }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Box display="flex" alignItems="center" mb={2}>
            <Box sx={{ mr: 2, color: 'primary.main' }}>
              {icon}
            </Box>
            <Typography variant="h6" fontWeight="bold">
              {title}
            </Typography>
          </Box>
          {children}
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Settings ⚙️
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <SettingCard title="Notifications" icon={<Notifications />}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.notifications}
                  onChange={(e) => handleSettingChange('notifications', e.target.checked)}
                />
              }
              label="Enable notifications"
            />
            <Typography variant="body2" color="text.secondary" mt={1}>
              Get notified when Pomodoro sessions start, end, or when it's break time.
            </Typography>
          </SettingCard>

          <SettingCard title="Audio" icon={<VolumeUp />}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.sound}
                  onChange={(e) => handleSettingChange('sound', e.target.checked)}
                />
              }
              label="Enable sound effects"
            />
            <Typography variant="body2" color="text.secondary" mt={1}>
              Play sounds when sessions start, end, or when transitioning to breaks.
            </Typography>
          </SettingCard>

          <SettingCard title="Timer Settings" icon={<Timer />}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Pomodoro Length"
                  type="number"
                  value={settings.pomodoroLength}
                  onChange={(e) => handleSettingChange('pomodoroLength', parseInt(e.target.value))}
                  InputProps={{ endAdornment: 'min' }}
                  inputProps={{ min: 15, max: 60 }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Short Break"
                  type="number"
                  value={settings.shortBreakLength}
                  onChange={(e) => handleSettingChange('shortBreakLength', parseInt(e.target.value))}
                  InputProps={{ endAdornment: 'min' }}
                  inputProps={{ min: 3, max: 15 }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Long Break"
                  type="number"
                  value={settings.longBreakLength}
                  onChange={(e) => handleSettingChange('longBreakLength', parseInt(e.target.value))}
                  InputProps={{ endAdornment: 'min' }}
                  inputProps={{ min: 10, max: 30 }}
                />
              </Grid>
            </Grid>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.autoBreak}
                  onChange={(e) => handleSettingChange('autoBreak', e.target.checked)}
                />
              }
              label="Auto-start breaks"
              sx={{ mt: 2 }}
            />
          </SettingCard>
        </Grid>

        <Grid item xs={12} md={6}>
          <SettingCard title="Appearance" icon={<Palette />}>
            <TextField
              select
              fullWidth
              label="Theme"
              value={settings.theme}
              onChange={(e) => handleSettingChange('theme', e.target.value)}
              sx={{ mb: 2 }}
            >
              <MenuItem value="dark">Dark</MenuItem>
              <MenuItem value="light">Light</MenuItem>
              <MenuItem value="auto">Auto (System)</MenuItem>
            </TextField>
            
            <TextField
              select
              fullWidth
              label="Language"
              value={settings.language}
              onChange={(e) => handleSettingChange('language', e.target.value)}
            >
              <MenuItem value="en">English</MenuItem>
              <MenuItem value="es">Español</MenuItem>
              <MenuItem value="fr">Français</MenuItem>
              <MenuItem value="de">Deutsch</MenuItem>
            </TextField>
          </SettingCard>

          <SettingCard title="Integrations" icon={<CloudSync />}>
            <Button
              variant="outlined"
              onClick={() => setSpotifyDialog(true)}
              sx={{ mb: 2, width: '100%' }}
            >
              Configure Spotify
            </Button>
            <Typography variant="body2" color="text.secondary">
              Connect your Spotify account to play focus music during Pomodoro sessions.
            </Typography>
          </SettingCard>

          <SettingCard title="Data & Privacy" icon={<Security />}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Button variant="outlined" onClick={exportData} fullWidth>
                  Export Data
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button variant="outlined" onClick={importData} fullWidth>
                  Import Data
                </Button>
              </Grid>
            </Grid>
            <Typography variant="body2" color="text.secondary" mt={2}>
              Export your data for backup or import from another device.
            </Typography>
          </SettingCard>
        </Grid>
      </Grid>

      {/* Spotify Configuration Dialog */}
      <Dialog open={spotifyDialog} onClose={() => setSpotifyDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Spotify Configuration</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            To enable Spotify integration, you'll need to create a Spotify app and get your credentials.
          </Typography>
          <TextField
            fullWidth
            label="Client ID"
            value={spotifyConfig.clientId}
            onChange={(e) => setSpotifyConfig({ ...spotifyConfig, clientId: e.target.value })}
            sx={{ mb: 2, mt: 1 }}
          />
          <TextField
            fullWidth
            label="Client Secret"
            type="password"
            value={spotifyConfig.clientSecret}
            onChange={(e) => setSpotifyConfig({ ...spotifyConfig, clientSecret: e.target.value })}
          />
          <Typography variant="body2" color="text.secondary" mt={2}>
            Get these credentials from your Spotify App settings at{' '}
            <a href="https://developer.spotify.com/" target="_blank" rel="noopener noreferrer">
              developer.spotify.com
            </a>
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSpotifyDialog(false)}>Cancel</Button>
          <Button onClick={saveSpotifyConfig} variant="contained">
            Save Configuration
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Settings;
