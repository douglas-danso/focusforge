import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { useNotifications, useUIActions } from '@/stores/useUIStore';
import { Button } from './Button';

const iconMap = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
};

const colorMap = {
  success: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200',
  error: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200',
  warning: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-200',
  info: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200',
};

export default function NotificationContainer() {
  const notifications = useNotifications();
  const { removeNotification } = useUIActions();

  return (
    <div className="fixed top-4 right-4 z-50 space-y-3 max-w-sm w-full">
      <AnimatePresence>
        {notifications.map((notification) => {
          const Icon = iconMap[notification.type];
          
          return (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, x: 300, scale: 0.9 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 300, scale: 0.9 }}
              transition={{
                type: "spring",
                stiffness: 300,
                damping: 24,
              }}
              className={`
                relative overflow-hidden rounded-xl border p-4 shadow-medium backdrop-blur-sm
                ${colorMap[notification.type]}
              `}
            >
              {/* Background blur effect */}
              <div className="absolute inset-0 bg-white/80 dark:bg-black/80 backdrop-blur-sm" />
              
              {/* Content */}
              <div className="relative flex gap-3">
                <Icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
                
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm">
                    {notification.title}
                  </h4>
                  {notification.message && (
                    <p className="text-sm opacity-90 mt-1">
                      {notification.message}
                    </p>
                  )}
                  
                  {notification.action && (
                    <div className="mt-3">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={notification.action.onClick}
                        className="text-xs"
                      >
                        {notification.action.label}
                      </Button>
                    </div>
                  )}
                </div>

                {/* Close button */}
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-6 w-6 rounded-lg opacity-70 hover:opacity-100"
                  onClick={() => removeNotification(notification.id)}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>

              {/* Auto-dismiss progress bar */}
              {notification.duration && notification.duration > 0 && (
                <motion.div
                  className="absolute bottom-0 left-0 h-1 bg-current opacity-30"
                  initial={{ width: '100%' }}
                  animate={{ width: '0%' }}
                  transition={{ 
                    duration: notification.duration / 1000,
                    ease: 'linear'
                  }}
                />
              )}
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
