import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useSidebarOpen, useUIActions } from '@/stores/useUIStore';
import { useUserProfile } from '@/stores/useStoreStore';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: '📊', emoji: true },
  { name: 'Tasks', href: '/tasks', icon: '✅', emoji: true },
  { name: 'Focus Sessions', href: '/focus', icon: '🍅', emoji: true },
  { name: 'Analytics', href: '/analytics', icon: '📈', emoji: true },
  { name: 'Mood Tracker', href: '/mood', icon: '😊', emoji: true },
  { name: 'Rewards Store', href: '/store', icon: '🏆', emoji: true },
  { name: 'Spotify', href: '/spotify', icon: '🎵', emoji: true },
];

const bottomNavigation = [
  { name: 'Settings', href: '/settings', icon: '⚙️', emoji: true },
  { name: 'Profile', href: '/profile', icon: '👤', emoji: true },
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
      <aside
        className={`
          fixed left-0 top-0 h-screen bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 z-50
          ${sidebarOpen ? 'w-[280px]' : '-translate-x-full lg:translate-x-0 lg:w-[280px]'}
          transition-transform duration-300 ease-in-out
          lg:relative lg:z-auto
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                <span className="text-white font-bold text-xl">🔥</span>
              </div>
              <span className="font-bold text-xl text-gray-900 dark:text-gray-100">FocusForge</span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;

              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200
                    ${isActive
                      ? 'bg-primary-500 text-white shadow-md'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800'
                    }
                  `}
                >
                  <span className="text-xl flex-shrink-0">{item.icon}</span>
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>

          {/* Bottom navigation */}
          <div className="px-4 py-4 border-t border-gray-200 dark:border-gray-700 space-y-1">
            {bottomNavigation.map((item) => {
              const isActive = location.pathname === item.href;

              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200
                    ${isActive
                      ? 'bg-primary-500 text-white shadow-md'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800'
                    }
                  `}
                >
                  <span className="text-xl flex-shrink-0">{item.icon}</span>
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </div>
        </div>
      </aside>

      {/* Mobile bottom navigation */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 z-50">
        <div className="flex justify-around items-center h-16 px-2">
          {navigation.slice(0, 5).map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <NavLink
                key={item.name}
                to={item.href}
                className={`
                  flex flex-col items-center justify-center flex-1 h-full transition-colors duration-200
                  ${isActive ? 'text-primary-500' : 'text-gray-500 dark:text-gray-400'}
                `}
              >
                <span className="text-2xl mb-1">{item.icon}</span>
              </NavLink>
            );
          })}
        </div>
      </div>
    </>
  );
}
