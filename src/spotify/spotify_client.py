import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from src.core.settings import settings

load_dotenv()

def get_spotify():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="playlist-modify-public user-read-playback-state user-modify-playback-state"
        
    ))

def play_playlist(playlist_uri):
    sp = get_spotify()
    devices = sp.devices()
    if not devices['devices']:
        print("No active Spotify device found.")
        return
    device_id = devices['devices'][0]['id']
    sp.start_playback(device_id=device_id, context_uri=playlist_uri)
    print("🎵 Ritual music started.")
