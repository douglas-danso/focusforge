import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../stores/useAuthStore';
import { useUIActions } from '../stores/useUIStore';
import LoadingScreen from '../components/ui/LoadingScreen';
import { apiService } from '../services/api';

export const AuthCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { googleAuthCallback } = useAuthStore();
  const { addNotification } = useUIActions();
  const [isProcessing, setIsProcessing] = useState(true);

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        const code = searchParams.get('code');
        const error = searchParams.get('error');

        if (error) {
          addNotification({
            type: 'error',
            title: 'Authentication Error',
            message: 'Failed to authenticate with Google. Please try again.',
          });
          navigate('/login');
          return;
        }

        if (!code) {
          addNotification({
            type: 'error',
            title: 'Authentication Error',
            message: 'No authorization code received. Please try again.',
          });
          navigate('/login');
          return;
        }

        // Process the OAuth callback
        await googleAuthCallback(code);
        
        addNotification({
          type: 'success',
          title: 'Welcome!',
          message: 'Successfully authenticated with Google.',
        });

        navigate('/dashboard');
      } catch (error) {
        console.error('Auth callback error:', error);
        addNotification({
          type: 'error',
          title: 'Authentication Failed',
          message: 'An error occurred during authentication. Please try again.',
        });
        navigate('/login');
      } finally {
        setIsProcessing(false);
      }
    };

    handleAuthCallback();
  }, [searchParams, navigate, googleAuthCallback, addNotification]);

  if (isProcessing) {
    return (
      <LoadingScreen 
        message="Completing authentication..." 
        fullScreen={true}
      />
    );
  }

  return null;
};
