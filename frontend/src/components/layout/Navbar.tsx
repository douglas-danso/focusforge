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
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between h-16 px-6">
        {/* Left side - Search */}
        <div className="flex items-center space-x-4 flex-1 max-w-md">
          <div className="relative w-full">
            <Input
              placeholder="Search tasks, moods, or rituals..."
              className="pl-10 bg-white/50 dark:bg-gray-900/50"
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
                className="absolute -top-1 -right-1 w-5 h-5 bg-blue-600 text-white text-xs font-bold rounded-full flex items-center justify-center"
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
                className="min-w-[8rem] bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 rounded-xl border border-gray-200 dark:border-gray-700 shadow-lg p-1 z-50"
                align="end"
                sideOffset={5}
              >
                <DropdownMenu.Item
                  className="flex items-center px-3 py-2 text-sm rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100 outline-none"
                  onClick={() => handleThemeChange('light')}
                >
                  <Sun className="h-4 w-4 mr-2" />
                  Light
                </DropdownMenu.Item>
                <DropdownMenu.Item
                  className="flex items-center px-3 py-2 text-sm rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100 outline-none"
                  onClick={() => handleThemeChange('dark')}
                >
                  <Moon className="h-4 w-4 mr-2" />
                  Dark
                </DropdownMenu.Item>
                <DropdownMenu.Item
                  className="flex items-center px-3 py-2 text-sm rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100 outline-none"
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
                  <div className="w-8 h-8 rounded-xl bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center">
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
                className="min-w-[12rem] bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 rounded-xl border border-gray-200 dark:border-gray-700 shadow-lg p-1 z-50"
                align="end"
                sideOffset={5}
              >
                <div className="px-3 py-2 border-b border-gray-200 dark:border-gray-700 mb-1">
                  <p className="font-medium text-sm">{user?.name}</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">{user?.email}</p>
                </div>

                <DropdownMenu.Item
                  className="flex items-center px-3 py-2 text-sm rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100 outline-none"
                  onClick={() => {/* Navigate to profile */}}
                >
                  <User className="h-4 w-4 mr-2" />
                  Profile
                </DropdownMenu.Item>

                <DropdownMenu.Item
                  className="flex items-center px-3 py-2 text-sm rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100 outline-none"
                  onClick={() => {/* Navigate to settings */}}
                >
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </DropdownMenu.Item>

                <DropdownMenu.Separator className="h-px bg-gray-200 dark:bg-gray-700 my-1" />

                <DropdownMenu.Item
                  className="flex items-center px-3 py-2 text-sm rounded-lg cursor-pointer hover:bg-red-100 dark:hover:bg-red-900/20 hover:text-red-900 dark:hover:text-red-100 outline-none text-red-600 dark:text-red-400"
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
