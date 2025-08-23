import React from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Bell,
  Plus,
  Moon,
  Sun,
  Monitor,
  LogOut,
  User,
  Settings,
} from 'lucide-react';
import { useAuth, useAuthActions } from '@/stores/useAuthStore';
import { useTheme, useUIActions } from '@/stores/useUIStore';
import { useActiveRewards } from '@/stores/useStoreStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';

export default function Navbar() {
  const { user } = useAuth();
  const { logout } = useAuthActions();
  const theme = useTheme();
  const { setTheme, addNotification } = useUIActions();
  const activeRewards = useActiveRewards();

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme);
    addNotification({
      type: 'info',
      title: 'Theme Updated',
      message: `Switched to ${newTheme} theme`
    });
  };

  const handleLogout = () => {
    logout();
    addNotification({
      type: 'info',
      title: 'Logged Out',
      message: 'See you next time!'
    });
  };

  const getThemeIcon = () => {
    switch (theme) {
      case 'dark':
        return Moon;
      case 'light':
        return Sun;
      default:
        return Monitor;
    }
  };

  const ThemeIcon = getThemeIcon();

  return (
    <header className="bg-card border-b border-border">
      <div className="flex items-center justify-between h-16 px-6">
        {/* Left side - Search */}
        <div className="flex items-center space-x-4 flex-1 max-w-md">
          <div className="relative w-full">
            <Input
              placeholder="Search tasks, moods, or rituals..."
              className="pl-10 bg-background/50"
              leftIcon={<Search className="h-4 w-4" />}
            />
          </div>
        </div>

        {/* Right side - Actions */}
        <div className="flex items-center space-x-3">
          {/* Quick add button */}
          <Button size="sm" className="hidden sm:flex">
            <Plus className="h-4 w-4 mr-2" />
            Add Task
          </Button>

          {/* Notifications */}
          <div className="relative">
            <Button size="icon" variant="ghost">
              <Bell className="h-5 w-5" />
            </Button>
            {activeRewards?.length > 0 && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-1 -right-1 w-5 h-5 bg-primary text-primary-foreground text-xs font-bold rounded-full flex items-center justify-center"
              >
                {activeRewards.length}
              </motion.div>
            )}
          </div>

          {/* Theme selector */}
          <DropdownMenu.Root>
            <DropdownMenu.Trigger asChild>
              <Button size="icon" variant="ghost">
                <ThemeIcon className="h-5 w-5" />
              </Button>
            </DropdownMenu.Trigger>

            <DropdownMenu.Portal>
              <DropdownMenu.Content
                className="min-w-[8rem] bg-popover text-popover-foreground rounded-xl border border-border shadow-large p-1 z-50"
                align="end"
                sideOffset={5}
              >
                <DropdownMenu.Item
                  className="flex items-center px-3 py-2 text-sm rounded-lg cursor-pointer hover:bg-accent hover:text-accent-foreground outline-none"
                  onClick={() => handleThemeChange('light')}
                >
                  <Sun className="h-4 w-4 mr-2" />
                  Light
                </DropdownMenu.Item>
                <DropdownMenu.Item
                  className="flex items-center px-3 py-2 text-sm rounded-lg cursor-pointer hover:bg-accent hover:text-accent-foreground outline-none"
                  onClick={() => handleThemeChange('dark')}
                >
                  <Moon className="h-4 w-4 mr-2" />
                  Dark
                </DropdownMenu.Item>
                <DropdownMenu.Item
                  className="flex items-center px-3 py-2 text-sm rounded-lg cursor-pointer hover:bg-accent hover:text-accent-foreground outline-none"
                  onClick={() => handleThemeChange('system')}
                >
                  <Monitor className="h-4 w-4 mr-2" />
                  System
                </DropdownMenu.Item>
              </DropdownMenu.Content>
            </DropdownMenu.Portal>
          </DropdownMenu.Root>

          {/* User menu */}
          <DropdownMenu.Root>
            <DropdownMenu.Trigger asChild>
              <Button variant="ghost" className="flex items-center space-x-2 px-2">
                {user?.picture ? (
                  <img
                    src={user.picture}
                    alt={user.name}
                    className="w-8 h-8 rounded-xl object-cover"
                  />
                ) : (
                  <div className="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center">
                    <User className="h-4 w-4" />
                  </div>
                )}
                <span className="hidden sm:block font-medium text-sm">
                  {user?.name?.split(' ')[0]}
                </span>
              </Button>
            </DropdownMenu.Trigger>

            <DropdownMenu.Portal>
              <DropdownMenu.Content
                className="min-w-[12rem] bg-popover text-popover-foreground rounded-xl border border-border shadow-large p-1 z-50"
                align="end"
                sideOffset={5}
              >
                <div className="px-3 py-2 border-b border-border mb-1">
                  <p className="font-medium text-sm">{user?.name}</p>
                  <p className="text-xs text-muted-foreground">{user?.email}</p>
                </div>

                <DropdownMenu.Item
                  className="flex items-center px-3 py-2 text-sm rounded-lg cursor-pointer hover:bg-accent hover:text-accent-foreground outline-none"
                  onClick={() => {/* Navigate to profile */}}
                >
                  <User className="h-4 w-4 mr-2" />
                  Profile
                </DropdownMenu.Item>

                <DropdownMenu.Item
                  className="flex items-center px-3 py-2 text-sm rounded-lg cursor-pointer hover:bg-accent hover:text-accent-foreground outline-none"
                  onClick={() => {/* Navigate to settings */}}
                >
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </DropdownMenu.Item>

                <DropdownMenu.Separator className="h-px bg-border my-1" />

                <DropdownMenu.Item
                  className="flex items-center px-3 py-2 text-sm rounded-lg cursor-pointer hover:bg-destructive hover:text-destructive-foreground outline-none text-red-600 dark:text-red-400"
                  onClick={handleLogout}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign out
                </DropdownMenu.Item>
              </DropdownMenu.Content>
            </DropdownMenu.Portal>
          </DropdownMenu.Root>
        </div>
      </div>
    </header>
  );
}
