from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import SpotifyPlaylistSearch, SpotifyPlaylistCreate
from app.services.spotify_service import SpotifyService
from app.core.database import get_database

router = APIRouter()

@router.post("/play/{playlist_uri}")
async def play_playlist(
    playlist_uri: str,
    user_id: str = "default",  # TODO: Get from auth
):
    """Play a Spotify playlist"""
    try:
        spotify_service = SpotifyService()
        result = await spotify_service.play_playlist(playlist_uri)
        return {"message": "Playlist started", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pause")
async def pause_playback(
    user_id: str = "default",  # TODO: Get from auth
):
    """Pause Spotify playback"""
    try:
        spotify_service = SpotifyService()
        result = await spotify_service.pause_playback()
        return {"message": "Playback paused", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/next")
async def next_track(
    user_id: str = "default",  # TODO: Get from auth
):
    """Skip to next track"""
    try:
        spotify_service = SpotifyService()
        result = await spotify_service.next_track()
        return {"message": "Skipped to next track", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_playlists(
    search_data: SpotifyPlaylistSearch,
    user_id: str = "default",  # TODO: Get from auth
):
    """Search Spotify playlists"""
    try:
        spotify_service = SpotifyService()
        results = await spotify_service.search_playlists(search_data.query, search_data.limit)
        return {"playlists": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-playlist")
async def create_playlist(
    playlist_data: SpotifyPlaylistCreate,
    user_id: str = "default",  # TODO: Get from auth
):
    """Create a new Spotify playlist"""
    try:
        spotify_service = SpotifyService()
        playlist_uri = await spotify_service.create_playlist(
            playlist_data.name,
            playlist_data.public,
            playlist_data.description
        )
        return {"message": "Playlist created", "playlist_uri": playlist_uri}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/play-by-mood/{mood}")
async def play_by_mood(
    mood: str,
    user_id: str = "default",  # TODO: Get from auth
):
    """Play playlist based on mood"""
    try:
        spotify_service = SpotifyService()
        result = await spotify_service.play_playlist_by_mood(mood)
        return {"message": f"Playing playlist for mood: {mood}", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
