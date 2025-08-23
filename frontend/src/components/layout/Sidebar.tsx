import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  CheckSquare,
  Heart,
  Store,
  Sparkles,
  Calendar,
  User,
  Settings,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useSidebarOpen, useUIActions } from '@/stores/useUIStore';
import { useUserProfile } from '@/stores/useStoreStore';
import { Button } from '@/components/ui/Button';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Tasks', href: '/tasks', icon: CheckSquare },
  { name: 'Mood', href: '/mood', icon: Heart },
  { name: 'Store', href: '/store', icon: Store },
  { name: 'Rituals', href: '/rituals', icon: Sparkles },
  { name: 'Calendar', href: '/calendar', icon: Calendar },
];

const bottomNavigation = [
  { name: 'Profile', href: '/profile', icon: User },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar() {
  const sidebarOpen = useSidebarOpen();
  const { toggleSidebar } = useUIActions();
  const location = useLocation();
  const userProfile = useUserProfile();

  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => toggleSidebar()}
        />
      )}

      {/* Sidebar */}
      <motion.aside
        animate={{
          width: sidebarOpen ? 256 : 64,
          x: sidebarOpen ? 0 : 0,
        }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className={`
          fixed left-0 top-0 h-screen bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 z-50
          ${sidebarOpen ? 'w-64' : 'w-16'}
          lg:relative lg:z-auto
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <motion.div
              animate={{
                opacity: sidebarOpen ? 1 : 0,
                x: sidebarOpen ? 0 : -20,
              }}
              transition={{ duration: 0.2 }}
              className="flex items-center space-x-3"
            >
              <div className="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">F</span>
              </div>
              {sidebarOpen && (
                <span className="font-bold text-lg text-gray-900 dark:text-gray-100">FocusForge</span>
              )}
            </motion.div>

            <Button
              size="icon"
              variant="ghost"
              onClick={toggleSidebar}
              className="h-8 w-8"
            >
              {sidebarOpen ? (
                <ChevronLeft className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* Currency display */}
          {sidebarOpen && userProfile && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 border-b border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-center space-x-3 bg-blue-100 dark:bg-blue-900/20 rounded-xl p-3">
                <div className="w-8 h-8 rounded-full bg-blue-200 dark:bg-blue-800 flex items-center justify-center">
                  <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                    {userProfile.currency_balance.toLocaleString()}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Balance</p>
                  <p className="font-bold text-lg text-blue-600 dark:text-blue-400">
                    {userProfile.currency_balance.toLocaleString()}
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-200 ${isActive ? 'text-blue-600 bg-blue-100 dark:bg-blue-900/20 hover:bg-blue-150' : ''} ${
                      !sidebarOpen ? 'justify-center' : ''
                    }`
                  }
                >
                  <item.icon className="h-5 w-5 flex-shrink-0" />
                  {sidebarOpen && (
                    <motion.span
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 }}
                    >
                      {item.name}
                    </motion.span>
                  )}
                  
                  {/* Active indicator */}
                  {isActive && !sidebarOpen && (
                    <motion.div
                      layoutId="sidebar-active"
                      className="absolute right-0 w-1 h-6 bg-blue-600 rounded-l-full"
                    />
                  )}
                </NavLink>
              );
            })}
          </nav>

          {/* Bottom navigation */}
          <div className="px-4 py-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
            {bottomNavigation.map((item) => {
              const isActive = location.pathname === item.href;
              
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-200 ${isActive ? 'text-blue-600 bg-blue-100 dark:bg-blue-900/20 hover:bg-blue-150' : ''} ${
                      !sidebarOpen ? 'justify-center' : ''
                    }`
                  }
                >
                  <item.icon className="h-5 w-5 flex-shrink-0" />
                  {sidebarOpen && (
                    <motion.span
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 }}
                    >
                      {item.name}
                    </motion.span>
                  )}
                </NavLink>
              );
            })}
          </div>
        </div>
      </motion.aside>
    </>
  );
}
