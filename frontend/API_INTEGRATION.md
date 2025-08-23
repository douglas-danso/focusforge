# FocusForge Frontend API Integration

This document describes how the FocusForge frontend integrates with the backend API, including authentication, error handling, and all available endpoints.

## 🚀 Quick Start

The frontend is now fully integrated with your backend API running on `http://localhost:8000`. All API calls include proper authentication, error handling, and loading states.

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `frontend` directory:

```bash
# Backend API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1

# Google OAuth Configuration
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
VITE_GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback

# Spotify Configuration (if using)
VITE_SPOTIFY_CLIENT_ID=your_spotify_client_id_here

# Feature Flags
VITE_ENABLE_SPOTIFY_INTEGRATION=true
VITE_ENABLE_GOOGLE_CALENDAR=true
VITE_DEBUG_MODE=false
VITE_MOCK_API=false
```

## 🏗️ Architecture

### API Service Layer (`src/services/api.ts`)

The core API service provides:
- **Axios instance** with interceptors for authentication and error handling
- **Standardized response types** (`ApiResponse<T>`, `PaginatedResponse<T>`)
- **Custom error handling** with `ApiError` class
- **Automatic token management** and 401 handling

### API Integration Hook (`src/hooks/useApi.ts`)

A React hook that provides:
- **Consistent error handling** across all API calls
- **Loading state management** for UI feedback
- **Success/error notifications** via toast messages
- **Type-safe API access** for all services

### Zustand Stores

All stores now integrate with the backend:
- **`useAuthStore`** - Authentication and user management
- **`useTaskStore`** - Task CRUD and Pomodoro operations
- **`useMoodStore`** - Mood logging and analytics
- **`useStoreStore`** - Store items and gamification
- **`useUIStore`** - UI state and notifications

## 🔐 Authentication Flow

### 1. Google OAuth Login

```typescript
import { useApi } from '../hooks/useApi';

const { auth } = useApi();

// Handle OAuth callback
const handleAuthCallback = async (code: string) => {
  const result = await auth.googleCallback(code);
  if (result) {
    // User is now authenticated
    // Token is automatically stored in useAuthStore
  }
};
```

### 2. Automatic Token Management

- **Request Interceptor**: Automatically adds `Authorization: Bearer <token>` to all requests
- **Response Interceptor**: Handles 401 errors by logging out user and redirecting to login
- **Token Refresh**: Automatic token refresh when needed

### 3. Protected Routes

```typescript
import { useAuthStore } from '../stores/useAuthStore';

const { isAuthenticated, isLoading } = useAuthStore();

if (isLoading) return <LoadingScreen />;
if (!isAuthenticated) return <Navigate to="/login" />;
```

## 📡 Available API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /google/callback` - Google OAuth callback
- `GET /me` - Get current user
- `POST /refresh` - Refresh access token
- `POST /logout` - Logout user

### Tasks (`/api/v1/tasks`)
- `GET /` - Get all tasks with filters
- `GET /dashboard` - Get dashboard tasks
- `GET /{id}` - Get single task
- `POST /` - Create new task
- `PUT /{id}` - Update task
- `DELETE /{id}` - Delete task
- `POST /{id}/blocks/{blockId}/start` - Start task block
- `POST /{id}/blocks/{blockId}/complete` - Complete task block
- `GET /{id}/guidance` - Get AI task guidance
- `GET /{id}/motivation` - Get motivational support

### Mood Tracking (`/api/v1/mood`)
- `POST /log` - Log mood entry
- `GET /history` - Get mood history
- `GET /insights` - Get mood insights
- `GET /analytics` - Get mood analytics

### Store & Gamification (`/api/v1/store`)
- `GET /items` - Get store items
- `GET /profile` - Get user profile and currency
- `POST /purchase/{itemName}` - Purchase item
- `GET /rewards/active` - Get active rewards
- `POST /rewards/{rewardId}/use` - Use reward
- `GET /stats` - Get user statistics
- `GET /insights/spending` - Get spending insights
- `GET /leaderboard` - Get leaderboard

### Rituals (`/api/v1/rituals`)
- `GET /templates` - Get ritual templates
- `GET /user` - Get user rituals
- `POST /` - Create ritual
- `PUT /{id}` - Update ritual
- `DELETE /{id}` - Delete ritual
- `POST /{id}/execute` - Execute ritual
- `GET /{id}/analytics` - Get ritual analytics

### Calendar (`/api/v1/calendar`)
- `GET /events` - Get calendar events
- `POST /events` - Create calendar event
- `PUT /events/{id}` - Update calendar event
- `DELETE /events/{id}` - Delete calendar event
- `POST /sync` - Sync with Google Calendar
- `GET /sync/status` - Get sync status

### Analytics (`/api/v1/analytics`)
- `GET /productivity` - Get productivity analytics
- `GET /focus-sessions` - Get focus session analytics
- `GET /mood-correlation` - Get mood correlation analytics

### Spotify Integration (`/api/v1/spotify`)
- `GET /playlists` - Get user playlists
- `GET /search` - Search playlists
- `POST /play` - Play music
- `GET /playback` - Get current playback

### Orchestrator (`/api/v1/orchestrator`)
- `POST /tasks/create-enhanced` - Create enhanced task with AI
- `POST /tasks/complete-enhanced` - Complete enhanced task
- `GET /daily-optimization` - Get daily optimization
- `POST /focus-session` - Start focus session
- `GET /status` - Get orchestrator status

## 💡 Usage Examples

### Creating a Task

```typescript
import { useApi } from '../hooks/useApi';

const { tasks } = useApi();

const handleCreateTask = async (taskData: CreateTaskData) => {
  const result = await tasks.createTask(taskData);
  if (result) {
    // Task created successfully
    // UI will show success notification automatically
  }
};
```

### Fetching Dashboard Data

```typescript
import { useApi } from '../hooks/useApi';
import { useEffect } from 'react';

const { tasks, store } = useApi();

useEffect(() => {
  // Fetch dashboard data on component mount
  tasks.getDashboardTasks();
  store.getUserProfile();
}, []);
```

### Error Handling

```typescript
import { useUIStore } from '../stores/useUIStore';

const { errors, clearError } = useUIStore();

// Display error in UI
if (errors.tasks) {
  return (
    <div className="error">
      {errors.tasks}
      <button onClick={() => clearError('tasks')}>Dismiss</button>
    </div>
  );
}
```

### Loading States

```typescript
import { useUIStore } from '../stores/useUIStore';

const { loadingStates } = useUIStore();

// Show loading spinner
if (loadingStates.tasks) {
  return <LoadingSpinner />;
}
```

## 🔄 Data Flow

### 1. User Action
User performs an action (e.g., creates a task)

### 2. API Call
Component calls appropriate API method via `useApi` hook

### 3. Loading State
UI shows loading indicator via `useUIStore`

### 4. Backend Processing
Request sent to backend with authentication token

### 5. Response Handling
- **Success**: Data updated in Zustand store, success notification shown
- **Error**: Error stored in UI store, error notification shown

### 6. UI Update
Component re-renders with new data from store

## 🛡️ Error Handling

### Automatic Error Handling
- **Network errors**: Automatic retry with exponential backoff
- **Authentication errors**: Automatic logout and redirect
- **Validation errors**: User-friendly error messages
- **Server errors**: Fallback error messages

### Custom Error Handling
```typescript
try {
  const result = await tasks.createTask(taskData);
  // Handle success
} catch (error) {
  if (error instanceof ApiError) {
    // Handle specific API errors
    switch (error.status) {
      case 400:
        // Handle validation error
        break;
      case 403:
        // Handle permission error
        break;
      case 500:
        // Handle server error
        break;
    }
  }
}
```

## 📱 Mobile Optimization

### Touch Gestures
- **Swipe actions** on task lists
- **Pull to refresh** on data lists
- **Long press** for context menus
- **Pinch to zoom** on charts

### Responsive Design
- **Mobile-first** approach
- **Breakpoint-based** layouts
- **Touch-friendly** button sizes
- **Optimized** for small screens

## 🎨 UI Components

### Animated Components
- **`AnimatedCard`** - Cards with hover effects and animations
- **`AnimatedButton`** - Buttons with ripple effects and states
- **`SwipeableCard`** - Cards with swipe gestures
- **`BottomSheet`** - Mobile-friendly modal replacement

### Loading States
- **Skeleton loaders** for content
- **Progress bars** for operations
- **Spinners** for quick actions
- **Skeletons** for lists and grids

## 🧪 Testing

### API Mocking
Set `VITE_MOCK_API=true` to use mock data instead of real API calls.

### Error Simulation
The API service includes error simulation for testing error handling.

### Development Tools
- **React Query DevTools** for API state inspection
- **Zustand DevTools** for state management debugging
- **Network tab** for API call monitoring

## 🚀 Performance

### Optimizations
- **Request deduplication** for concurrent API calls
- **Automatic caching** of frequently accessed data
- **Lazy loading** of non-critical components
- **Debounced search** for better UX

### Monitoring
- **API response times** tracking
- **Error rate** monitoring
- **User interaction** analytics
- **Performance metrics** collection

## 🔧 Troubleshooting

### Common Issues

#### 1. CORS Errors
Ensure backend allows requests from `http://localhost:3000`

#### 2. Authentication Failures
Check token expiration and refresh logic

#### 3. Network Timeouts
Verify backend is running and accessible

#### 4. Type Errors
Ensure API response types match frontend interfaces

### Debug Mode
Set `VITE_DEBUG_MODE=true` for detailed logging and error information.

## 📚 Additional Resources

- **Backend API Documentation**: See `backend/BACKEND_FEATURES_AND_FLOW.md`
- **Component Library**: See `src/components/ui/`
- **State Management**: See `src/stores/`
- **Type Definitions**: See `src/types/`

## 🤝 Contributing

When adding new API endpoints:
1. Add to `src/services/api.ts`
2. Add to `src/hooks/useApi.ts`
3. Update relevant Zustand stores
4. Add TypeScript interfaces
5. Update this documentation

---

The frontend is now fully connected to your backend API! All features should work with real data, and you'll get proper error handling, loading states, and user feedback throughout the application.
