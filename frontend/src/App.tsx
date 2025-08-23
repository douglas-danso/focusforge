import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Layout components
import Layout from './components/layout/Layout';
import PublicLayout from './components/layout/PublicLayout';

// Pages
import Login from './pages/Login';
import { AuthCallback } from './pages/AuthCallback';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Mood from './pages/Mood';
import Store from './pages/Store';
import Rituals from './pages/Rituals';
import Calendar from './pages/Calendar';
import Profile from './pages/Profile';
import TaskDetail from './pages/TaskDetail';

// Components
import ProtectedRoute from './components/auth/ProtectedRoute';
import NotificationContainer from './components/ui/NotificationContainer';

// Stores
import { useAuthStore } from './stores/useAuthStore';
import { useUIStore } from './stores/useUIStore';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const { isAuthenticated, isLoading } = useAuthStore();
  const { setTheme } = useUIStore();

  useEffect(() => {
    // Initialize theme
    const savedTheme = localStorage.getItem('focusforge-ui') 
      ? JSON.parse(localStorage.getItem('focusforge-ui')!).state.theme 
      : 'system';
    setTheme(savedTheme);
  }, [setTheme]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Routes>
            {/* Public routes */}
            <Route path="/" element={
              <PublicLayout>
                {isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />}
              </PublicLayout>
            } />
            
            <Route path="/login" element={
              <PublicLayout>
                {isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />}
              </PublicLayout>
            } />
            
            <Route path="/auth/callback" element={<AuthCallback />} />

            {/* Protected routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/tasks" element={
              <ProtectedRoute>
                <Layout>
                  <Tasks />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/tasks/:id" element={
              <ProtectedRoute>
                <Layout>
                  <TaskDetail />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/mood" element={
              <ProtectedRoute>
                <Layout>
                  <Mood />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/store" element={
              <ProtectedRoute>
                <Layout>
                  <Store />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/rituals" element={
              <ProtectedRoute>
                <Layout>
                  <Rituals />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/calendar" element={
              <ProtectedRoute>
                <Layout>
                  <Calendar />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/profile" element={
              <ProtectedRoute>
                <Layout>
                  <Profile />
                </Layout>
              </ProtectedRoute>
            } />

            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>

          {/* Global components */}
          <NotificationContainer />
        </div>
      </Router>
      
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
