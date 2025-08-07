from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.models.schemas import SpotifyPlaylistSearch, SpotifyPlaylistCreate
from app.services.spotify_service import SpotifyService
from app.core.database import get_database

router = APIRouter()

# Pydantic models for auth endpoints
class AuthCodeRequest(BaseModel):
    authorization_code: str

class AuthUrlResponse(BaseModel):
    auth_url: str
    instructions: str
    setup_required: bool

class TrackSearchRequest(BaseModel):
    query: str
    limit: int = 10

class PlaylistTracksRequest(BaseModel):
    playlist_uri: str

# Health and Status Endpoints
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@router.get("/status")
async def get_spotify_status() -> Dict[str, Any]:
    """
    Get current Spotify service status and capabilities
    Shows what features are available based on auth level
    """
    spotify_service = SpotifyService()
    status = spotify_service.get_status()
    
    # Add capability information
    status["capabilities"] = {
        "search": spotify_service.configured,
        "public_playlists": spotify_service.configured,
        "playback_control": spotify_service.user_configured,
        "playlist_creation": spotify_service.user_configured,
        "private_playlists": spotify_service.user_configured,
        "current_playback": spotify_service.user_configured
    }
    
    return status

@router.post("/test-connection")
async def test_spotify_connection():
    """
    Test Spotify connection and return available features
    """
    spotify_service = SpotifyService()
    
    if not spotify_service.configured:
        return {
            "connected": False,
            "message": "Spotify client credentials not configured. Please set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET.",
            "available_features": []
        }
    
    try:
        # Test basic search functionality
        playlists = await spotify_service.search_playlists("test", limit=1)
        
        available_features = ["search", "public_playlists", "track_search"]
        if spotify_service.user_configured:
            available_features.extend(["playbook_control", "playlist_creation", "private_playlists", "current_playback"])
        
        return {
            "connected": True,
            "client_credentials": True,
            "user_auth": spotify_service.user_configured,
            "available_features": available_features,
            "message": "Spotify connection working ✅"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Connection test failed: {str(e)}"
        )

# Authentication Setup Endpoints
@router.get("/auth-url", response_model=AuthUrlResponse)
async def get_spotify_auth_url():
    """
    Get Spotify authorization URL for manual authentication setup.
    This is needed once to enable full Spotify features (playback control, etc.)
    """
    spotify_service = SpotifyService()
    
    if not spotify_service.configured:
        raise HTTPException(
            status_code=500, 
            detail="Spotify client credentials not configured. Please set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET."
        )
    
    if spotify_service.user_configured:
        return AuthUrlResponse(
            auth_url="",
            instructions="User authentication already configured! Full Spotify features are available.",
            setup_required=False
        )
    
    auth_url = spotify_service.generate_auth_url()
    
    return AuthUrlResponse(
        auth_url=auth_url,
        instructions=(
            "🔐 To enable full Spotify features:\n"
            "1. Visit the provided URL and authorize the application\n"
            "2. Copy the 'code' parameter from the redirect URL\n"
            "3. POST the code to /api/v1/spotify/setup-auth\n"
            "4. Restart the container for changes to take effect"
        ),
        setup_required=True
    )

@router.post("/setup-auth")
async def setup_spotify_auth(request: AuthCodeRequest):
    """
    Complete Spotify user authentication setup using authorization code.
    This enables playback control, playlist creation, private playlists, etc.
    """
    spotify_service = SpotifyService()
    
    if not spotify_service.configured:
        raise HTTPException(
            status_code=500,
            detail="Spotify client credentials not configured"
        )
    
    try:
        result = spotify_service.setup_user_auth_from_code(request.authorization_code)
        
        if "successful" in result:
            return {
                "success": True, 
                "message": result,
                "next_steps": "Authentication setup complete! You may need to restart the container for all features to be available."
            }
        else:
            raise HTTPException(status_code=400, detail=result)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")

# Playback Control Endpoints
@router.get("/current-playback")
async def get_current_playback():
    """
    Get current playback information (requires user auth)
    """
    spotify_service = SpotifyService()
    result = await spotify_service.get_current_playback()
    
    if "error" in result:
        if "authentication required" in result["error"].lower():
            raise HTTPException(
                status_code=401, 
                detail="User authentication required. Use /spotify/auth-url to set up."
            )
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/play/{playlist_uri}")
async def play_playlist(
    playlist_uri: str,
    user_id: str = "default",
    device_id: Optional[str] = Query(None, description="Specific device ID to play on")
):
    """Play a Spotify playlist (requires user auth)"""
    try:
        spotify_service = SpotifyService()
        result = await spotify_service.play_playlist(playlist_uri, device_id)
        
        # Check if result indicates auth is needed
        if "authorization" in result:
            raise HTTPException(
                status_code=401,
                detail={
                    "message": result,
                    "auth_url_endpoint": "/api/v1/spotify/auth-url"
                }
            )
        
        return {"message": "Playlist command sent", "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pause")
async def pause_playback(
    user_id: str = "default",
    device_id: Optional[str] = Query(None, description="Specific device ID")
):
    """Pause Spotify playback (requires user auth)"""
    try:
        spotify_service = SpotifyService()
        result = await spotify_service.pause_playback(device_id)
        
        if "authorization" in result:
            raise HTTPException(
                status_code=401,
                detail={
                    "message": result,
                    "auth_url_endpoint": "/api/v1/spotify/auth-url"
                }
            )
        
        return {"message": "Playback pause command sent", "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/next")
async def next_track(
    user_id: str = "default",
    device_id: Optional[str] = Query(None, description="Specific device ID")
):
    """Skip to next track (requires user auth)"""
    try:
        spotify_service = SpotifyService()
        result = await spotify_service.next_track(device_id)
        
        if "authorization" in result:
            raise HTTPException(
                status_code=401,
                detail={
                    "message": result,
                    "auth_url_endpoint": "/api/v1/spotify/auth-url"
                }
            )
        
        return {"message": "Next track command sent", "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/play-by-mood/{mood}")
async def play_by_mood(
    mood: str,
    user_id: str = "default",
    device_id: Optional[str] = Query(None, description="Specific device ID")
):
    """Play playlist based on mood (searches publicly, but requires user auth to play)"""
    try:
        spotify_service = SpotifyService()
        result = await spotify_service.play_playlist_by_mood(mood)
        
        if "authorization" in result:
            raise HTTPException(
                status_code=401,
                detail={
                    "message": result,
                    "auth_url_endpoint": "/api/v1/spotify/auth-url"
                }
            )
        
        return {"message": f"Mood playlist command sent for: {mood}", "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search and Discovery Endpoints (Work without user auth)
@router.post("/search/playlists")
async def search_playlists(
    search_data: SpotifyPlaylistSearch,
    user_id: str = "default",
):
    """Search Spotify playlists (works with client credentials)"""
    try:
        spotify_service = SpotifyService()
        
        if not spotify_service.configured:
            raise HTTPException(
                status_code=503,
                detail="Spotify not configured. Please set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET."
            )
        
        results = await spotify_service.search_playlists(search_data.query, search_data.limit)
        return {
            "playlists": results,
            "query": search_data.query,
            "count": len(results)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/tracks")
async def search_tracks(
    search_data: TrackSearchRequest,
    user_id: str = "default",
):
    """Search Spotify tracks (works with client credentials)"""
    try:
        spotify_service = SpotifyService()
        
        if not spotify_service.configured:
            raise HTTPException(
                status_code=503,
                detail="Spotify not configured. Please set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET."
            )
        
        results = await spotify_service.search_tracks(search_data.query, search_data.limit)
        return {
            "tracks": results,
            "query": search_data.query,
            "count": len(results)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/playlist/tracks")
async def get_playlist_tracks(
    request: PlaylistTracksRequest,
    user_id: str = "default",
):
    """Get tracks from a playlist (works with client credentials for public playlists)"""
    try:
        spotify_service = SpotifyService()
        
        if not spotify_service.configured:
            raise HTTPException(
                status_code=503,
                detail="Spotify not configured. Please set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET."
            )
        
        tracks = await spotify_service.get_playlist_tracks(request.playlist_uri)
        return {
            "tracks": tracks,
            "playlist_uri": request.playlist_uri,
            "count": len(tracks)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Playlist Management Endpoints (Require user auth)
@router.post("/create-playlist")
async def create_playlist(
    playlist_data: SpotifyPlaylistCreate,
    user_id: str = "default",
):
    """Create a new Spotify playlist (requires user auth)"""
    try:
        spotify_service = SpotifyService()
        result = await spotify_service.create_playlist(
            playlist_data.name,
            playlist_data.public,
            playlist_data.description
        )
        
        if "authorization" in result:
            raise HTTPException(
                status_code=401,
                detail={
                    "message": result,
                    "auth_url_endpoint": "/api/v1/spotify/auth-url"
                }
            )
        
        return {"message": "Playlist creation command sent", "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Backward compatibility - keep the original search endpoint
@router.post("/search")
async def search_playlists_legacy(
    search_data: SpotifyPlaylistSearch,
    user_id: str = "default",
):
    """Search Spotify playlists (legacy endpoint for backward compatibility)"""
    return await search_playlists(search_data, user_id)