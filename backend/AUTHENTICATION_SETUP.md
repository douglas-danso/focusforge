# FocusForge Authentication Setup

This document explains how to set up Google OAuth authentication for the FocusForge backend.

## Overview

FocusForge uses Google OAuth 2.0 for user authentication with JWT tokens for session management. This provides:

- Secure authentication through Google
- No need for users to create separate passwords
- JWT tokens for stateless authentication
- Automatic user profile creation from Google data

## Environment Variables Required

Create a `.env` file in the backend directory with these variables:

```bash
# JWT Authentication
SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_EXPIRATION_HOURS=24

# Google OAuth Configuration (Required)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Database
MONGODB_URI=mongodb://mongo:27017
DATABASE_NAME=focusforge

# OpenAI (for AI features)
OPENAI_API_KEY=your-openai-api-key
```

## Google OAuth Setup

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Create a new project or select existing one

2. **Enable Google+ API**
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
   - Also enable "Google OAuth2 API"

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8000/api/v1/auth/google/callback`
     - `http://127.0.0.1:8000/api/v1/auth/google/callback`
   - Copy the Client ID and Client Secret

4. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Fill in required fields (app name, user support email, etc.)
   - Add scopes: email, profile, openid

## API Endpoints

### Authentication Endpoints

- `GET /api/v1/auth/status` - Check auth system status
- `GET /api/v1/auth/google/url` - Get Google OAuth URL
- `POST /api/v1/auth/google/callback` - Handle OAuth callback
- `GET /api/v1/auth/me` - Get current user info
- `GET /api/v1/auth/verify` - Verify token validity
- `POST /api/v1/auth/logout` - Logout (client-side token removal)

### Protected Endpoints

All other endpoints now require authentication:
- `GET /api/v1/tasks/` - Get user tasks
- `POST /api/v1/tasks/` - Create task
- `GET /api/v1/mood/` - Get mood logs
- etc.

## Authentication Flow

1. **Get Google OAuth URL**
   ```bash
   curl http://localhost:8000/api/v1/auth/google/url
   ```

2. **User visits OAuth URL and grants permission**
   - User is redirected to Google
   - After approval, Google redirects to callback URL with code

3. **Exchange code for JWT token**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/google/callback \
     -H "Content-Type: application/json" \
     -d '{"authorization_code": "received_auth_code"}'
   ```

4. **Use JWT token for API calls**
   ```bash
   curl -H "Authorization: Bearer your_jwt_token" \
     http://localhost:8000/api/v1/tasks/
   ```

## Testing Authentication

Run the test script to verify everything works:

```bash
cd backend
python test_auth.py
```

This will test:
- Authentication system status
- Public endpoints accessibility
- Protected endpoints security
- Google OAuth URL generation

## Frontend Integration

For frontend applications:

1. **Get OAuth URL from backend**
2. **Redirect user to Google OAuth**
3. **Handle callback and extract authorization code**
4. **Send code to backend callback endpoint**
5. **Store returned JWT token**
6. **Include token in all API requests**

Example JavaScript:

```javascript
// Get OAuth URL
const authResponse = await fetch('/api/v1/auth/google/url');
const { auth_url } = await authResponse.json();

// Redirect user
window.location.href = auth_url;

// After callback, exchange code for token
const tokenResponse = await fetch('/api/v1/auth/google/callback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ authorization_code: code })
});

const { token } = await tokenResponse.json();
localStorage.setItem('focusforge_token', token.access_token);

// Use token in API calls
const apiResponse = await fetch('/api/v1/tasks/', {
  headers: { 'Authorization': `Bearer ${token.access_token}` }
});
```

## Security Notes

- JWT tokens expire after 24 hours (configurable)
- Tokens are stateless and contain user ID
- All passwords are handled by Google OAuth
- HTTPS should be used in production
- Keep Google Client Secret secure and never expose to frontend

## Troubleshooting

### Common Issues

1. **"Google OAuth not configured" error**
   - Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set
   - Verify Google Cloud project has OAuth APIs enabled

2. **"Invalid authorization code" error**
   - Code may have expired (they expire quickly)
   - Check redirect URI matches exactly in Google Console

3. **"Authentication required" on protected endpoints**
   - Include `Authorization: Bearer <token>` header
   - Check token hasn't expired
   - Verify token format is correct

### Debug Mode

Set environment variable for more detailed logs:
```bash
export LOG_LEVEL=DEBUG
```

## Production Deployment

For production:

1. **Use HTTPS everywhere**
2. **Set secure JWT secret keys**
3. **Configure proper CORS origins**
4. **Set production Google OAuth redirect URIs**
5. **Use environment-specific configuration**

Example production redirect URI:
```
https://yourdomain.com/api/v1/auth/google/callback
```
