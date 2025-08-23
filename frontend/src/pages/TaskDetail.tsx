import React from 'react';
import { motion } from 'framer-motion';
import { useParams } from 'react-router-dom';

export default function TaskDetail() {
  const { taskId } = useParams();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8"
    >
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Task Detail</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Task ID: {taskId}
        </p>
      </div>

      <div className="text-center py-16">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
          Task Detail Page Coming Soon
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Detailed task view with AI insights, Pomodoro timer, and proof submission will be implemented here.
        </p>
      </div>
    </motion.div>
  );
}
