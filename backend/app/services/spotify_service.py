import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from typing import List, Tuple, Optional, Dict, Any
import asyncio
import os
import json
from datetime import datetime, timedelta
from app.core.config import settings

class SpotifyService:
    def __init__(self):
        self.sp = None
        self.configured = False
        self.user_auth_sp = None  # For user-specific operations
        self.user_configured = False
        self._initialize_spotify()
    
    def _initialize_spotify(self):
        """Initialize Spotify client with Client Credentials (no browser auth)"""
        # Check if Spotify credentials are configured
        if not settings.SPOTIPY_CLIENT_ID or not settings.SPOTIPY_CLIENT_SECRET:
            print("Spotify credentials not configured - Spotify features will be disabled")
            self.sp = None
            self.configured = False
            return
            
        try:
            auth_manager = SpotifyClientCredentials(
                client_id=settings.SPOTIPY_CLIENT_ID,
                client_secret=settings.SPOTIPY_CLIENT_SECRET
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            
            # Test the connection with a lightweight search
            test_result = self.sp.search(q="test", type="track", limit=1)
            self.configured = True
            print("✅ Spotify Client Credentials initialized successfully")
            
            # Try to initialize user auth if token file exists (optional)
            self._try_initialize_user_auth()
            
        except spotipy.exceptions.SpotifyException as e:
            print(f"❌ Spotify API error during initialization: {e}")
            self.sp = None
            self.configured = False
        except Exception as e:
            print(f"❌ Failed to initialize Spotify: {e}")
            self.sp = None
            self.configured = False
    
    def _try_initialize_user_auth(self):
        """Try to initialize user auth from existing token cache (Docker-friendly)"""
        try:
            # Look for cached token file
            cache_path = os.getenv('SPOTIFY_CACHE_PATH', '/app/data/.spotify_cache')
            
            if os.path.exists(cache_path):
                redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI', 'http://localhost:8080/callback')
                scope = os.getenv('SPOTIFY_SCOPE', 'user-read-playback-state user-modify-playback-state playlist-read-private playlist-modify-public')
                
                auth_manager = SpotifyOAuth(
                    client_id=settings.SPOTIPY_CLIENT_ID,
                    client_secret=settings.SPOTIPY_CLIENT_SECRET,
                    redirect_uri=redirect_uri,
                    scope=scope,
                    cache_path=cache_path,
                    open_browser=False
                )
                
                # Check if we have a valid cached token
                token = auth_manager.get_cached_token()
                if token and not auth_manager.is_token_expired(token):
                    self.user_auth_sp = spotipy.Spotify(auth_manager=auth_manager)
                    self.user_configured = True
                    print("✅ Spotify User Authentication loaded from cache")
                else:
                    print("⚠️  Cached Spotify token expired or invalid")
                    
        except Exception as e:
            print(f"ℹ️  User auth not available (cache not found): {e}")
    
    def generate_auth_url(self) -> str:
        """Generate authorization URL for manual user authentication setup"""
        try:
            redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI', 'http://localhost:8080/callback')
            scope = os.getenv('SPOTIFY_SCOPE', 'user-read-playback-state user-modify-playback-state playlist-read-private playlist-modify-public')
            
            auth_manager = SpotifyOAuth(
                client_id=settings.SPOTIPY_CLIENT_ID,
                client_secret=settings.SPOTIPY_CLIENT_SECRET,
                redirect_uri=redirect_uri,
                scope=scope,
                open_browser=False
            )
            
            auth_url = auth_manager.get_authorize_url()
            return f"To enable full Spotify features, visit: {auth_url}"
            
        except Exception as e:
            return f"Error generating auth URL: {e}"
    
    def setup_user_auth_from_code(self, authorization_code: str) -> str:
        """Setup user authentication from authorization code (for initial Docker setup)"""
        try:
            cache_path = os.getenv('SPOTIFY_CACHE_PATH', '/app/data/.spotify_cache')
            redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI', 'http://localhost:8080/callback')
            scope = os.getenv('SPOTIFY_SCOPE', 'user-read-playback-state user-modify-playback-state playlist-read-private playlist-modify-public')
            
            # Ensure cache directory exists
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            
            auth_manager = SpotifyOAuth(
                client_id=settings.SPOTIPY_CLIENT_ID,
                client_secret=settings.SPOTIPY_CLIENT_SECRET,
                redirect_uri=redirect_uri,
                scope=scope,
                cache_path=cache_path,
                open_browser=False
            )
            
            token = auth_manager.get_access_token(authorization_code)
            if token:
                self.user_auth_sp = spotipy.Spotify(auth_manager=auth_manager)
                self.user_configured = True
                return "✅ User authentication setup successful! Full Spotify features now available."
            else:
                return "❌ Failed to get access token"
                
        except Exception as e:
            return f"❌ Error setting up user auth: {e}"
    
    async def get_current_playback(self) -> Dict[str, Any]:
        """Get current playback information (requires user auth)"""
        if not self.user_configured:
            return {"error": "User authentication required for playback info"}
        
        try:
            current = self.user_auth_sp.current_playback()
            if current and current.get('item'):
                return {
                    "is_playing": current['is_playing'],
                    "track": current['item']['name'],
                    "artist": current['item']['artists'][0]['name'],
                    "album": current['item']['album']['name'],
                    "progress_ms": current['progress_ms'],
                    "duration_ms": current['item']['duration_ms']
                }
            return {"error": "No active playback"}
        except Exception as e:
            return {"error": f"Error getting playback info: {e}"}
    
    async def play_playlist(self, playlist_uri: str, device_id: Optional[str] = None) -> str:
        """Play a Spotify playlist (requires user auth)"""
        if not self.configured:
            return "❌ Spotify not configured. Please add SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET to your environment variables."
        
        if not self.user_configured:
            auth_info = self.generate_auth_url()
            return f"⚠️  Spotify playback control requires user authorization. {auth_info}"
        
        try:
            # Start playback
            self.user_auth_sp.start_playback(
                context_uri=playlist_uri,
                device_id=device_id
            )
            return f"✅ Playing playlist: {playlist_uri}"
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 404:
                return "❌ No active Spotify device found. Please open Spotify on a device first."
            return f"❌ Error playing playlist: {str(e)}"
        except Exception as e:
            return f"❌ Error playing playlist: {str(e)}"
    
    async def pause_playback(self, device_id: Optional[str] = None) -> str:
        """Pause Spotify playback (requires user auth)"""
        if not self.user_configured:
            return "⚠️  Spotify playback control requires user authorization"
        
        try:
            self.user_auth_sp.pause_playback(device_id=device_id)
            return "⏸️  Playback paused"
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 404:
                return "❌ No active Spotify device found"
            return f"❌ Error pausing playback: {str(e)}"
        except Exception as e:
            return f"❌ Error pausing playback: {str(e)}"
    
    async def next_track(self, device_id: Optional[str] = None) -> str:
        """Skip to next track (requires user auth)"""
        if not self.user_configured:
            return "⚠️  Spotify playback control requires user authorization"
        
        try:
            self.user_auth_sp.next_track(device_id=device_id)
            return "⏭️  Skipped to next track"
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 404:
                return "❌ No active Spotify device found"
            return f"❌ Error skipping track: {str(e)}"
        except Exception as e:
            return f"❌ Error skipping track: {str(e)}"
    
    async def search_playlists(self, query: str, limit: int = 10) -> List[Tuple[str, str]]:
        """Search Spotify playlists (works with Client Credentials)"""
        if not self.configured:
            return []
        
        try:
            results = self.sp.search(q=query, type='playlist', limit=limit)
            playlists = results['playlists']['items']
            return [(pl['name'], pl['uri']) for pl in playlists if pl]
        except Exception as e:
            print(f"❌ Error searching playlists: {e}")
            return []
    
    async def search_tracks(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """Search Spotify tracks (works with Client Credentials)"""
        if not self.configured:
            return []
        
        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = results['tracks']['items']
            return [
                {
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'uri': track['uri'],
                    'preview_url': track['preview_url']
                }
                for track in tracks if track
            ]
        except Exception as e:
            print(f"❌ Error searching tracks: {e}")
            return []
    
    async def get_playlist_tracks(self, playlist_uri: str) -> List[Dict[str, str]]:
        """Get tracks from a playlist (works with Client Credentials for public playlists)"""
        if not self.configured:
            return []
        
        try:
            # Extract playlist ID from URI
            playlist_id = playlist_uri.split(':')[-1]
            results = self.sp.playlist_tracks(playlist_id)
            
            tracks = []
            for item in results['items']:
                if item['track'] and item['track']['name']:
                    tracks.append({
                        'name': item['track']['name'],
                        'artist': ', '.join([artist['name'] for artist in item['track']['artists']]),
                        'album': item['track']['album']['name'],
                        'uri': item['track']['uri']
                    })
            return tracks
        except Exception as e:
            print(f"❌ Error getting playlist tracks: {e}")
            return []
    
    async def create_playlist(self, name: str, public: bool = True, description: str = "") -> str:
        """Create a new Spotify playlist (requires user auth)"""
        if not self.configured:
            return "❌ Spotify not configured. Please add SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET to your environment variables."
        
        if not self.user_configured:
            auth_info = self.generate_auth_url()
            return f"⚠️  Spotify playlist creation requires user authorization. {auth_info}"
        
        try:
            user_id = self.user_auth_sp.current_user()['id']
            playlist = self.user_auth_sp.user_playlist_create(
                user_id, name, public=public, description=description
            )
            return f"✅ Created playlist '{name}': {playlist['external_urls']['spotify']}"
        except Exception as e:
            return f"❌ Error creating playlist: {str(e)}"
    
    async def play_playlist_by_mood(self, mood: str) -> str:
        """Play playlist based on mood"""
        mood_map = {
            'happy': 'Happy Hits',
            'focus': 'Deep Focus', 
            'chill': 'Chill Hits',
            'sad': 'Life Sucks',
            'energetic': 'Power Workout',
            'relaxed': 'Peaceful Piano',
            'motivated': 'Workout Motivation',
            'study': 'Lofi Hip Hop',
            'party': 'Party Hits',
            'sleep': 'Sleep Sounds'
        }
        
        query = mood_map.get(mood.lower(), mood)
        playlists = await self.search_playlists(query, limit=3)
        
        if playlists:
            result = await self.play_playlist(playlists[0][1])
            return f"🎵 Playing playlist for mood '{mood}': {playlists[0][0]}. {result}"
        else:
            return f"❌ No playlist found for mood '{mood}'"
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status information"""
        return {
            "client_credentials_configured": self.configured,
            "user_auth_configured": self.user_configured,
            "client_id_set": bool(getattr(settings, 'SPOTIPY_CLIENT_ID', None)),
            "client_secret_set": bool(getattr(settings, 'SPOTIPY_CLIENT_SECRET', None)),
            "auth_setup_url": self.generate_auth_url() if self.configured and not self.user_configured else None
        }