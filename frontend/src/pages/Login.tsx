
import { motion } from 'framer-motion';
import { Chrome, Sparkles, Target, Brain, Zap } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { useUIActions } from '@/stores/useUIStore';

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Task Breakdown',
    description: 'Smart task analysis and 25-minute Pomodoro blocks',
  },
  {
    icon: Target,
    title: 'Mood-Driven Productivity',
    description: 'Track mood patterns and optimize your focus sessions',
  },
  {
    icon: Sparkles,
    title: 'Custom Focus Rituals',
    description: 'Guided preparation with meditation and Spotify integration',
  },
  {
    icon: Zap,
    title: 'Gamified Rewards',
    description: 'Earn currency for task completion and unlock rewards',
  },
];

export default function Login() {
  const { addNotification } = useUIActions();

  const handleGoogleLogin = () => {
    try {
      // In a real app, this would redirect to the backend OAuth endpoint
      const googleAuthUrl = `${import.meta.env.VITE_GOOGLE_REDIRECT_URI || 'http://localhost:8004'}/api/v1/auth/google/url`;
      window.location.href = googleAuthUrl;
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Login Error',
        message: 'Failed to initiate Google login'
      });
    }
  };

  return (
    <div className="container-padding">
      <div className="max-w-6xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center min-h-screen py-8">
          {/* Hero section */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-8"
          >
            {/* Logo and brand */}
            <div className="space-y-4">
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2, duration: 0.5 }}
                className="flex items-center space-x-3"
              >
                <div className="w-12 h-12 rounded-2xl bg-blue-600 flex items-center justify-center">
                  <span className="text-white font-bold text-xl">F</span>
                </div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">FocusForge</h1>
              </motion.div>
              
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.5 }}
                className="text-xl text-gray-600 dark:text-gray-400 leading-relaxed"
              >
                Transform your productivity with AI-powered task management, 
                mood tracking, and personalized focus rituals.
              </motion.p>
            </div>

            {/* Features grid */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
              className="grid sm:grid-cols-2 gap-4"
            >
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8 + index * 0.1, duration: 0.5 }}
                  className="flex space-x-3 p-4 rounded-xl bg-white/50 dark:bg-gray-900/50 border border-gray-200/50 dark:border-gray-700/50"
                >
                  <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center flex-shrink-0">
                    <feature.icon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <h3 className="font-medium text-sm text-gray-900 dark:text-gray-100">
                      {feature.title}
                    </h3>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      {feature.description}
                    </p>
                  </div>
                </motion.div>
              ))}
            </motion.div>

            {/* Stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2, duration: 0.5 }}
              className="flex space-x-8 pt-4"
            >
              <div>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">25min</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Focus blocks</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">AI</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Task analysis</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">∞</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Possibilities</p>
              </div>
            </motion.div>
          </motion.div>

          {/* Login card */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex justify-center lg:justify-end"
          >
            <Card className="w-full max-w-md">
              <CardHeader className="text-center space-y-4">
                <CardTitle className="text-2xl">Welcome back</CardTitle>
                <CardDescription>
                  Sign in to continue your productivity journey
                </CardDescription>
              </CardHeader>
              
              <CardContent className="space-y-6">
                {/* Google login button */}
                <Button
                  onClick={handleGoogleLogin}
                  size="lg"
                  className="w-full"
                  icon={<Chrome className="h-5 w-5" />}
                >
                  Continue with Google
                </Button>

                {/* Divider */}
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-200 dark:border-gray-700" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-white dark:bg-gray-900 px-2 text-gray-600 dark:text-gray-400">
                      Quick & secure
                    </span>
                  </div>
                </div>

                {/* Benefits */}
                <div className="space-y-3 text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Join thousands of users who have transformed their productivity
                  </p>
                  
                  <div className="flex justify-center space-x-6 text-xs text-gray-600 dark:text-gray-400">
                    <span>✓ No password required</span>
                    <span>✓ Instant setup</span>
                    <span>✓ Sync across devices</span>
                  </div>
                </div>

                {/* Demo hint */}
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl">
                  <p className="text-sm text-center text-blue-700 dark:text-blue-300">
                    💡 First time? Your AI productivity coach will guide you through setup
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
