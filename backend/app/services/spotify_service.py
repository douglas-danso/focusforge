import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Tuple
from app.core.config import settings

class SpotifyService:
    def __init__(self):
        self.sp = None
        self._initialize_spotify()
    
    def _initialize_spotify(self):
        """Initialize Spotify client"""
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=settings.SPOTIPY_CLIENT_ID,
                client_secret=settings.SPOTIPY_CLIENT_SECRET,
                redirect_uri=settings.SPOTIPY_REDIRECT_URI,
                scope=(
                    "playlist-modify-public user-read-playback-state "
                    "user-modify-playback-state"
                )
            ))
        except Exception as e:
            print(f"Failed to initialize Spotify: {e}")
            self.sp = None
    
    async def play_playlist(self, playlist_uri: str) -> str:
        """Play a Spotify playlist"""
        if not self.sp:
            return "Spotify not configured"
        
        try:
            devices = self.sp.devices()
            if not devices['devices']:
                return "No active Spotify device found"
            
            device_id = devices['devices'][0]['id']
            self.sp.start_playback(device_id=device_id, context_uri=playlist_uri)
            return "Playlist started successfully"
        except Exception as e:
            return f"Error playing playlist: {str(e)}"
    
    async def pause_playback(self) -> str:
        """Pause Spotify playback"""
        if not self.sp:
            return "Spotify not configured"
        
        try:
            self.sp.pause_playback()
            return "Playback paused"
        except Exception as e:
            return f"Error pausing playback: {str(e)}"
    
    async def next_track(self) -> str:
        """Skip to next track"""
        if not self.sp:
            return "Spotify not configured"
        
        try:
            self.sp.next_track()
            return "Skipped to next track"
        except Exception as e:
            return f"Error skipping track: {str(e)}"
    
    async def search_playlists(self, query: str, limit: int = 5) -> List[Tuple[str, str]]:
        """Search Spotify playlists"""
        if not self.sp:
            return []
        
        try:
            results = self.sp.search(q=query, type='playlist', limit=limit)
            playlists = results['playlists']['items']
            return [(pl['name'], pl['uri']) for pl in playlists]
        except Exception as e:
            print(f"Error searching playlists: {e}")
            return []
    
    async def create_playlist(self, name: str, public: bool = True, description: str = "") -> str:
        """Create a new Spotify playlist"""
        if not self.sp:
            return "Spotify not configured"
        
        try:
            user_id = self.sp.me()['id']
            playlist = self.sp.user_playlist_create(
                user=user_id, 
                name=name, 
                public=public, 
                description=description
            )
            return playlist['uri']
        except Exception as e:
            return f"Error creating playlist: {str(e)}"
    
    async def play_playlist_by_mood(self, mood: str) -> str:
        """Play playlist based on mood"""
        mood_map = {
            'happy': 'Happy Hits',
            'focus': 'Deep Focus',
            'chill': 'Chill Hits',
            'sad': 'Life Sucks',
            'energetic': 'Power Workout',
            'relaxed': 'Peaceful Piano',
            'motivated': 'Workout Motivation'
        }
        
        query = mood_map.get(mood.lower(), mood)
        playlists = await self.search_playlists(query)
        
        if playlists:
            result = await self.play_playlist(playlists[0][1])
            return f"Playing playlist for mood '{mood}': {playlists[0][0]}. {result}"
        else:
            return f"No playlist found for mood '{mood}'"
