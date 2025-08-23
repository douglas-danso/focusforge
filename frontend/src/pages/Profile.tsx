import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  User, 
  Settings, 
  Bell, 
  Moon, 
  Sun, 
  Music, 
  Calendar, 
  Download, 
  Upload, 
  Trash2, 
  Edit3,
  Save,
  X,
  CheckCircle,
  AlertCircle,
  Shield,
  Palette,
  Smartphone,
  Globe,
  Database
} from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { AnimatedCard, ElevatedCard, GlassCard } from '../components/ui/AnimatedCard';
import { AnimatedButton, PrimaryButton, IconButton } from '../components/ui/AnimatedButton';
import { BottomSheet } from '../components/ui/MobileOptimized';
import { useAuthStore } from '../stores/useAuthStore';
import { useUIStore } from '../stores/useUIStore';
import { useIsMobile } from '../hooks/useMediaQuery';

interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  notifications: {
    email: boolean;
    push: boolean;
    inApp: boolean;
    sound: boolean;
    vibration: boolean;
  };
  privacy: {
    shareAnalytics: boolean;
    shareUsageData: boolean;
    allowTracking: boolean;
  };
  integrations: {
    spotify: boolean;
    googleCalendar: boolean;
    slack: boolean;
  };
  accessibility: {
    highContrast: boolean;
    reducedMotion: boolean;
    fontSize: 'small' | 'medium' | 'large';
  };
}

const Profile: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'profile' | 'settings' | 'integrations' | 'data'>('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [showThemePicker, setShowThemePicker] = useState(false);
  const [showNotificationSettings, setShowNotificationSettings] = useState(false);
  const [showIntegrationSettings, setShowIntegrationSettings] = useState(false);
  
  const { user, logout } = useAuthStore();
  const { theme, setTheme, addNotification } = useUIStore();
  const isMobile = useIsMobile();

  const [settings, setSettings] = useState<UserSettings>({
    theme: 'system',
    notifications: {
      email: true,
      push: true,
      inApp: true,
      sound: true,
      vibration: false,
    },
    privacy: {
      shareAnalytics: true,
      shareUsageData: false,
      allowTracking: false,
    },
    integrations: {
      spotify: false,
      googleCalendar: false,
      slack: false,
    },
    accessibility: {
      highContrast: false,
      reducedMotion: false,
      fontSize: 'medium',
    },
  });

  const [editForm, setEditForm] = useState({
    name: user?.name || '',
    email: user?.email || '',
    bio: '',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  });

  const handleSaveProfile = () => {
    // In a real app, this would update the user profile via API
    addNotification({
      type: 'success',
      title: 'Profile Updated',
      message: 'Profile updated successfully!'
    });
    setIsEditing(false);
  };

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setSettings(prev => ({ ...prev, theme: newTheme }));
    setTheme(newTheme);
    setShowThemePicker(false);
    addNotification({
      type: 'success',
      title: 'Theme Changed',
      message: `Theme changed to ${newTheme}`
    });
  };

  const handleNotificationToggle = (key: keyof UserSettings['notifications']) => {
    setSettings(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [key]: !prev.notifications[key],
      },
    }));
  };

  const handlePrivacyToggle = (key: keyof UserSettings['privacy']) => {
    setSettings(prev => ({
      ...prev,
      privacy: {
        ...prev.privacy,
        [key]: !prev.privacy[key],
      },
    }));
  };

  const handleIntegrationToggle = (key: keyof UserSettings['integrations']) => {
    setSettings(prev => ({
      ...prev,
      integrations: {
        ...prev.integrations,
        [key]: !prev.integrations[key],
      },
    }));
    
    addNotification({
      type: 'success',
      title: 'Integration',
      message: `${key.charAt(0).toUpperCase() + key.slice(1)} integration ${settings.integrations[key] ? 'disabled' : 'enabled'}`
    });
  };

  const handleAccessibilityToggle = (key: keyof UserSettings['accessibility']) => {
    setSettings(prev => ({
      ...prev,
      accessibility: {
        ...prev.accessibility,
        [key]: !prev.accessibility[key],
      },
    }));
  };

  const handleFontSizeChange = (size: 'small' | 'medium' | 'large') => {
    setSettings(prev => ({
      ...prev,
      accessibility: {
        ...prev.accessibility,
        fontSize: size,
      },
    }));
  };

  const exportData = () => {
    const data = {
      user: user,
      settings: settings,
      exportDate: new Date().toISOString(),
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `focusforge-data-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    addNotification({
      type: 'success',
      title: 'Data Export',
      message: 'Data exported successfully!'
    });
  };

  const deleteAccount = () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      // In a real app, this would call the API to delete the account
      logout();
      addNotification({
        type: 'success',
        title: 'Account Deleted',
        message: 'Account deleted successfully'
      });
    }
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'integrations', label: 'Integrations', icon: Globe },
    { id: 'data', label: 'Data', icon: Database },
  ];

  const renderProfileTab = () => (
    <div className="space-y-6">
      {/* Profile Header */}
      <ElevatedCard className="p-6">
        <div className="flex items-center space-x-6">
          <motion.div
            className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-3xl font-bold"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {user?.name?.charAt(0)?.toUpperCase() || 'U'}
          </motion.div>
          
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">{user?.name || 'User'}</h2>
            <p className="text-gray-600 mb-2">{user?.email || 'user@example.com'}</p>
            <p className="text-sm text-gray-500">Member since {new Date().toLocaleDateString()}</p>
          </div>
          
          <Button
            onClick={() => setIsEditing(true)}
            variant="outline"
            className="hidden md:flex"
          >
            <Edit3 className="w-4 h-4 mr-2" />
            Edit Profile
          </Button>
        </div>
      </ElevatedCard>

      {/* Profile Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">127</div>
          <div className="text-sm text-gray-600">Tasks Completed</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-green-600">23</div>
          <div className="text-sm text-gray-600">Day Streak</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">1,250</div>
          <div className="text-sm text-gray-600">Focus Points</div>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {[
            { action: 'Completed task', details: 'Design system review', time: '2 hours ago' },
            { action: 'Started focus session', details: 'Product planning', time: '4 hours ago' },
            { action: 'Logged mood', details: 'Feeling productive', time: '6 hours ago' },
            { action: 'Earned points', details: '+50 for completing milestone', time: '1 day ago' },
          ].map((activity, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div>
                <div className="font-medium text-gray-900">{activity.action}</div>
                <div className="text-sm text-gray-600">{activity.details}</div>
              </div>
              <div className="text-xs text-gray-500">{activity.time}</div>
            </motion.div>
          ))}
        </div>
      </Card>
    </div>
  );

  const renderSettingsTab = () => (
    <div className="space-y-6">
      {/* Theme Settings */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Palette className="w-5 h-5 mr-2" />
          Appearance
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(['light', 'dark', 'system'] as const).map((themeOption) => (
            <motion.div
              key={themeOption}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                settings.theme === themeOption
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => handleThemeChange(themeOption)}
            >
              <div className="text-center">
                <div className="text-2xl mb-2">
                  {themeOption === 'light' && <Sun className="w-8 h-8 mx-auto text-yellow-500" />}
                  {themeOption === 'dark' && <Moon className="w-8 h-8 mx-auto text-gray-700" />}
                  {themeOption === 'system' && <Settings className="w-8 h-8 mx-auto text-blue-500" />}
                </div>
                <div className="font-medium capitalize">{themeOption}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </Card>

      {/* Notification Settings */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Bell className="w-5 h-5 mr-2" />
          Notifications
        </h3>
        
        <div className="space-y-4">
          {Object.entries(settings.notifications).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between">
              <div>
                <div className="font-medium capitalize">{key.replace(/([A-Z])/g, ' $1')}</div>
                <div className="text-sm text-gray-600">
                  {key === 'email' && 'Receive email notifications'}
                  {key === 'push' && 'Show push notifications'}
                  {key === 'inApp' && 'Display in-app notifications'}
                  {key === 'sound' && 'Play notification sounds'}
                  {key === 'vibration' && 'Vibrate on notifications'}
                </div>
              </div>
              <Button
                variant={value ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleNotificationToggle(key as keyof UserSettings['notifications'])}
              >
                {value ? 'On' : 'Off'}
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* Privacy Settings */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Shield className="w-5 h-5 mr-2" />
          Privacy & Data
        </h3>
        
        <div className="space-y-4">
          {Object.entries(settings.privacy).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between">
              <div>
                <div className="font-medium capitalize">{key.replace(/([A-Z])/g, ' $1')}</div>
                <div className="text-sm text-gray-600">
                  {key === 'shareAnalytics' && 'Share anonymous usage analytics'}
                  {key === 'shareUsageData' && 'Share detailed usage data'}
                  {key === 'allowTracking' && 'Allow cross-site tracking'}
                </div>
              </div>
              <Button
                variant={value ? 'default' : 'outline'}
                size="sm"
                onClick={() => handlePrivacyToggle(key as keyof UserSettings['privacy'])}
              >
                {value ? 'On' : 'Off'}
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* Accessibility Settings */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Smartphone className="w-5 h-5 mr-2" />
          Accessibility
        </h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">High Contrast</div>
              <div className="text-sm text-gray-600">Increase contrast for better visibility</div>
            </div>
            <Button
              variant={settings.accessibility.highContrast ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleAccessibilityToggle('highContrast')}
            >
              {settings.accessibility.highContrast ? 'On' : 'Off'}
            </Button>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">Reduced Motion</div>
              <div className="text-sm text-gray-600">Minimize animations and transitions</div>
            </div>
            <Button
              variant={settings.accessibility.reducedMotion ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleAccessibilityToggle('reducedMotion')}
            >
              {settings.accessibility.reducedMotion ? 'On' : 'Off'}
            </Button>
          </div>
          
          <div>
            <div className="font-medium mb-2">Font Size</div>
            <div className="flex space-x-2">
              {(['small', 'medium', 'large'] as const).map((size) => (
                <Button
                  key={size}
                  variant={settings.accessibility.fontSize === size ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => handleFontSizeChange(size)}
                >
                  {size.charAt(0).toUpperCase() + size.slice(1)}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );

  const renderIntegrationsTab = () => (
    <div className="space-y-6">
      {/* Spotify Integration */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
              <Music className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Spotify</h3>
              <p className="text-gray-600">Connect your Spotify account for focus music</p>
            </div>
          </div>
          <Button
            variant={settings.integrations.spotify ? 'default' : 'outline'}
            onClick={() => handleIntegrationToggle('spotify')}
          >
            {settings.integrations.spotify ? 'Connected' : 'Connect'}
          </Button>
        </div>
      </Card>

      {/* Google Calendar Integration */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Google Calendar</h3>
              <p className="text-gray-600">Sync your calendar and schedule tasks</p>
            </div>
          </div>
          <Button
            variant={settings.integrations.googleCalendar ? 'default' : 'outline'}
            onClick={() => handleIntegrationToggle('googleCalendar')}
          >
            {settings.integrations.googleCalendar ? 'Connected' : 'Connect'}
          </Button>
        </div>
      </Card>

      {/* Slack Integration */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center">
              <Globe className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Slack</h3>
              <p className="text-gray-600">Get notifications and updates in Slack</p>
            </div>
          </div>
          <Button
            variant={settings.integrations.slack ? 'default' : 'outline'}
            onClick={() => handleIntegrationToggle('slack')}
          >
            {settings.integrations.slack ? 'Connected' : 'Connect'}
          </Button>
        </div>
      </Card>
    </div>
  );

  const renderDataTab = () => (
    <div className="space-y-6">
      {/* Data Export */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Download className="w-5 h-5 mr-2" />
          Export Your Data
        </h3>
        <p className="text-gray-600 mb-4">
          Download all your data including tasks, mood logs, and settings in JSON format.
        </p>
        <Button onClick={exportData} className="bg-green-600 hover:bg-green-700">
          <Download className="w-4 h-4 mr-2" />
          Export Data
        </Button>
      </Card>

      {/* Data Import */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Upload className="w-5 h-5 mr-2" />
          Import Data
        </h3>
        <p className="text-gray-600 mb-4">
          Import previously exported data to restore your settings and data.
        </p>
        <Button variant="outline">
          <Upload className="w-4 h-4 mr-2" />
          Choose File
        </Button>
      </Card>

      {/* Account Deletion */}
      <Card className="p-6 border-red-200 bg-red-50">
        <h3 className="text-lg font-semibold mb-4 flex items-center text-red-800">
          <Trash2 className="w-5 h-5 mr-2" />
          Delete Account
        </h3>
        <p className="text-red-700 mb-4">
          This action will permanently delete your account and all associated data. This cannot be undone.
        </p>
        <Button 
          onClick={deleteAccount}
          variant="destructive"
          className="bg-red-600 hover:bg-red-700"
        >
          <Trash2 className="w-4 h-4 mr-2" />
          Delete Account
        </Button>
      </Card>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Profile & Settings</h1>
          <p className="text-gray-600">Manage your account, preferences, and integrations</p>
        </motion.div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-white rounded-2xl p-1 mb-8 shadow-sm overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 py-3 px-4 rounded-xl font-medium transition-all duration-200 whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {activeTab === 'profile' && renderProfileTab()}
            {activeTab === 'settings' && renderSettingsTab()}
            {activeTab === 'integrations' && renderIntegrationsTab()}
            {activeTab === 'data' && renderDataTab()}
          </motion.div>
        </AnimatePresence>

        {/* Mobile Edit Profile Button */}
        {isMobile && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="fixed bottom-6 left-6 z-50"
          >
            <Button
              onClick={() => setIsEditing(true)}
              size="lg"
              className="w-14 h-14 rounded-full shadow-2xl bg-blue-600 hover:bg-blue-700 text-white"
            >
              <Edit3 className="w-6 h-6" />
            </Button>
          </motion.div>
        )}
      </div>

      {/* Edit Profile Modal/Bottom Sheet */}
      <BottomSheet
        isOpen={isEditing}
        onClose={() => setIsEditing(false)}
        title="Edit Profile"
        className="max-w-md mx-auto"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
            <Input
              value={editForm.name}
              onChange={(e) => setEditForm(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Your name"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <Input
              value={editForm.email}
              onChange={(e) => setEditForm(prev => ({ ...prev, email: e.target.value }))}
              placeholder="your@email.com"
              type="email"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
            <textarea
              value={editForm.bio}
              onChange={(e) => setEditForm(prev => ({ ...prev, bio: e.target.value }))}
              placeholder="Tell us about yourself..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent h-20 resize-none"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
            <select
              value={editForm.timezone}
              onChange={(e) => setEditForm(prev => ({ ...prev, timezone: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="UTC">UTC</option>
              <option value="America/New_York">Eastern Time</option>
              <option value="America/Chicago">Central Time</option>
              <option value="America/Denver">Mountain Time</option>
              <option value="America/Los_Angeles">Pacific Time</option>
              <option value="Europe/London">London</option>
              <option value="Europe/Paris">Paris</option>
              <option value="Asia/Tokyo">Tokyo</option>
            </select>
          </div>
          
          <div className="flex space-x-3 pt-4">
            <Button
              onClick={() => setIsEditing(false)}
              variant="outline"
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSaveProfile}
              className="flex-1 bg-blue-600 hover:bg-blue-700"
            >
              <Save className="w-4 h-4 mr-2" />
              Save
            </Button>
          </div>
        </div>
      </BottomSheet>
    </div>
  );
};

export default Profile;
