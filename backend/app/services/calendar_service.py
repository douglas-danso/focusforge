"""
Enhanced Calendar Service for FocusForge
Handles calendar integration with Google Calendar API and task scheduling
"""

import asyncio
import json
import os
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from bson import ObjectId
import logging

# Google Calendar imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.models.schemas import CalendarEvent, CalendarEventCreate
from app.core.config import settings
from app.core.database import get_database

logger = logging.getLogger(__name__)

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarIntegration:
    """Google Calendar API integration"""
    
    def __init__(self):
        self.credentials_cache = {}
        self.service_cache = {}
    
    def _get_credentials_path(self, user_id: str) -> str:
        """Get the path for user's Google credentials"""
        credentials_dir = getattr(settings, 'GOOGLE_CREDENTIALS_DIR', './credentials')
        os.makedirs(credentials_dir, exist_ok=True)
        return os.path.join(credentials_dir, f'google_calendar_{user_id}.json')
    
    def _get_client_config(self) -> Dict[str, Any]:
        """Get Google OAuth client configuration"""
        if not hasattr(settings, 'GOOGLE_CLIENT_ID') or not hasattr(settings, 'GOOGLE_CLIENT_SECRET'):
            raise ValueError("Google Calendar credentials not configured")
        
        return {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [getattr(settings, 'GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/google/callback')]
            }
        }
    
    def get_authorization_url(self, user_id: str) -> str:
        """Get Google OAuth authorization URL"""
        try:
            client_config = self._get_client_config()
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            flow.redirect_uri = client_config["web"]["redirect_uris"][0]
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=user_id
            )
            
            # Cache flow for later token exchange
            self.credentials_cache[f"flow_{user_id}"] = flow
            
            return auth_url
        except Exception as e:
            logger.error(f"Failed to get authorization URL: {e}")
            raise
    
    async def exchange_code_for_token(self, user_id: str, authorization_code: str) -> bool:
        """Exchange authorization code for access token"""
        try:
            flow = self.credentials_cache.get(f"flow_{user_id}")
            if not flow:
                # Recreate flow if not cached
                client_config = self._get_client_config()
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                flow.redirect_uri = client_config["web"]["redirect_uris"][0]
            
            # Exchange code for token
            flow.fetch_token(code=authorization_code)
            credentials = flow.credentials
            
            # Save credentials
            credentials_path = self._get_credentials_path(user_id)
            with open(credentials_path, 'w') as token_file:
                token_file.write(credentials.to_json())
            
            # Cache credentials
            self.credentials_cache[user_id] = credentials
            
            # Clean up flow cache
            if f"flow_{user_id}" in self.credentials_cache:
                del self.credentials_cache[f"flow_{user_id}"]
            
            return True
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {e}")
            return False
    
    def _get_credentials(self, user_id: str) -> Optional[Credentials]:
        """Get Google credentials for user"""
        # Check cache first
        if user_id in self.credentials_cache:
            return self.credentials_cache[user_id]
        
        credentials_path = self._get_credentials_path(user_id)
        credentials = None
        
        if os.path.exists(credentials_path):
            credentials = Credentials.from_authorized_user_file(credentials_path, SCOPES)
        
        # Refresh token if expired
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                # Save refreshed token
                with open(credentials_path, 'w') as token_file:
                    token_file.write(credentials.to_json())
            except Exception as e:
                logger.error(f"Failed to refresh credentials: {e}")
                return None
        
        if credentials and credentials.valid:
            self.credentials_cache[user_id] = credentials
            return credentials
        
        return None
    
    def _get_service(self, user_id: str):
        """Get Google Calendar service for user"""
        if user_id in self.service_cache:
            return self.service_cache[user_id]
        
        credentials = self._get_credentials(user_id)
        if not credentials:
            return None
        
        try:
            service = build('calendar', 'v3', credentials=credentials)
            self.service_cache[user_id] = service
            return service
        except Exception as e:
            logger.error(f"Failed to build Calendar service: {e}")
            return None
    
    async def create_event(self, user_id: str, event_data: Dict[str, Any]) -> Optional[str]:
        """Create event in Google Calendar"""
        service = self._get_service(user_id)
        if not service:
            return None
        
        try:
            # Convert to Google Calendar format
            google_event = {
                'summary': event_data['title'],
                'description': event_data.get('description', ''),
                'start': {
                    'dateTime': event_data['start_time'].isoformat(),
                    'timeZone': getattr(settings, 'TIMEZONE', 'UTC'),
                },
                'end': {
                    'dateTime': event_data['end_time'].isoformat(),
                    'timeZone': getattr(settings, 'TIMEZONE', 'UTC'),
                },
            }
            
            if event_data.get('location'):
                google_event['location'] = event_data['location']
            
            # Add reminders
            if event_data.get('reminder_minutes'):
                google_event['reminders'] = {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': event_data['reminder_minutes']},
                        {'method': 'popup', 'minutes': event_data['reminder_minutes']},
                    ],
                }
            
            result = await asyncio.to_thread(
                service.events().insert(calendarId='primary', body=google_event).execute
            )
            
            return result.get('id')
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create Google Calendar event: {e}")
            return None
    
    async def update_event(self, user_id: str, google_event_id: str, event_data: Dict[str, Any]) -> bool:
        """Update event in Google Calendar"""
        service = self._get_service(user_id)
        if not service:
            return False
        
        try:
            # Get existing event
            existing_event = await asyncio.to_thread(
                service.events().get(calendarId='primary', eventId=google_event_id).execute
            )
            
            # Update fields
            if 'title' in event_data:
                existing_event['summary'] = event_data['title']
            if 'description' in event_data:
                existing_event['description'] = event_data['description']
            if 'start_time' in event_data:
                existing_event['start']['dateTime'] = event_data['start_time'].isoformat()
            if 'end_time' in event_data:
                existing_event['end']['dateTime'] = event_data['end_time'].isoformat()
            if 'location' in event_data:
                existing_event['location'] = event_data['location']
            
            await asyncio.to_thread(
                service.events().update(
                    calendarId='primary', 
                    eventId=google_event_id, 
                    body=existing_event
                ).execute
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to update Google Calendar event: {e}")
            return False
    
    async def delete_event(self, user_id: str, google_event_id: str) -> bool:
        """Delete event from Google Calendar"""
        service = self._get_service(user_id)
        if not service:
            return False
        
        try:
            await asyncio.to_thread(
                service.events().delete(calendarId='primary', eventId=google_event_id).execute
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete Google Calendar event: {e}")
            return False
    
    async def get_events(self, user_id: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get events from Google Calendar"""
        service = self._get_service(user_id)
        if not service:
            return []
        
        try:
            events_result = await asyncio.to_thread(
                service.events().list(
                    calendarId='primary',
                    timeMin=start_time.isoformat() + 'Z',
                    timeMax=end_time.isoformat() + 'Z',
                    singleEvents=True,
                    orderBy='startTime'
                ).execute
            )
            
            events = events_result.get('items', [])
            formatted_events = []
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Handle all-day events
                if 'T' not in start:
                    start += 'T00:00:00'
                if 'T' not in end:
                    end += 'T23:59:59'
                
                formatted_event = {
                    'google_event_id': event['id'],
                    'title': event.get('summary', ''),
                    'description': event.get('description', ''),
                    'start_time': datetime.fromisoformat(start.replace('Z', '+00:00')),
                    'end_time': datetime.fromisoformat(end.replace('Z', '+00:00')),
                    'location': event.get('location', ''),
                }
                formatted_events.append(formatted_event)
            
            return formatted_events
        except Exception as e:
            logger.error(f"Failed to get Google Calendar events: {e}")
            return []

class CalendarService:
    def __init__(self, db=None):
        self.db = db
        self.collection = None
        self.google_calendar = GoogleCalendarIntegration()
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the calendar service"""
        if self.is_initialized:
            return
        
        if not self.db:
            self.db = await get_database()
        
        self.collection = self.db.calendar_events
        self.is_initialized = True
        logger.info("Calendar service initialized")
    
    async def get_google_auth_url(self, user_id: str) -> str:
        """Get Google Calendar authorization URL"""
        return self.google_calendar.get_authorization_url(user_id)
    
    async def authorize_google_calendar(self, user_id: str, authorization_code: str) -> bool:
        """Authorize Google Calendar integration"""
        return await self.google_calendar.exchange_code_for_token(user_id, authorization_code)
    
    async def is_google_calendar_connected(self, user_id: str) -> bool:
        """Check if user has connected Google Calendar"""
        credentials = self.google_calendar._get_credentials(user_id)
        return credentials is not None and credentials.valid
    
    async def create_event(self, user_id: str, event_data: CalendarEventCreate, sync_to_google: bool = True) -> CalendarEvent:
        """Create a new calendar event"""
        if not self.is_initialized:
            await self.initialize()
        
        event_dict = {
            "user_id": user_id,
            "title": event_data.title,
            "description": event_data.description or "",
            "start_time": event_data.start_time,
            "end_time": event_data.end_time,
            "location": event_data.location,
            "all_day": event_data.all_day,
            "recurring": event_data.recurring,
            "reminder_minutes": event_data.reminder_minutes,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "google_event_id": None,
            "synced_to_google": False
        }
        
        # Sync to Google Calendar if enabled and connected
        if sync_to_google and await self.is_google_calendar_connected(user_id):
            google_event_id = await self.google_calendar.create_event(user_id, event_dict)
            if google_event_id:
                event_dict["google_event_id"] = google_event_id
                event_dict["synced_to_google"] = True
        
        result = await self.collection.insert_one(event_dict)
        event_dict["_id"] = str(result.inserted_id)
        return CalendarEvent(**event_dict)
    
    async def create_task_calendar_events(self, user_id: str, task_id: str, task_title: str, blocks: List[Dict[str, Any]]) -> List[CalendarEvent]:
        """Create calendar events for task blocks"""
        if not self.is_initialized:
            await self.initialize()
        
        events = []
        
        for i, block in enumerate(blocks):
            # Calculate event times (user can customize these later)
            start_time = datetime.now() + timedelta(hours=i)  # Default: spread blocks hourly
            end_time = start_time + timedelta(minutes=block.get('duration_minutes', 25))
            
            event_data = CalendarEventCreate(
                title=f"🎯 {task_title} - Block {i+1}",
                description=f"Task block {i+1} of {len(blocks)}\n\nBlock Details:\n{block.get('description', '')}",
                start_time=start_time,
                end_time=end_time,
                location="Focus Zone",
                all_day=False,
                recurring=False,
                reminder_minutes=5
            )
            
            event = await self.create_event(user_id, event_data)
            
            # Link event to task block
            await self.db.task_blocks.update_one(
                {"_id": ObjectId(block["_id"])},
                {"$set": {"calendar_event_id": event.id}}
            )
            
            events.append(event)
        
        return events
    
    async def get_events(self, user_id: str, start_date: Optional[datetime] = None, 
                        end_date: Optional[datetime] = None, include_google: bool = True) -> List[CalendarEvent]:
        """Get calendar events for a user within a date range"""
        if not self.is_initialized:
            await self.initialize()
        
        query = {"user_id": user_id}
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["start_time"] = date_query
        
        # Get local events
        cursor = self.collection.find(query).sort("start_time", 1)
        events = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            events.append(CalendarEvent(**doc))
        
        # Get Google Calendar events if connected and requested
        if include_google and await self.is_google_calendar_connected(user_id):
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now() + timedelta(days=90)
            
            google_events = await self.google_calendar.get_events(user_id, start_date, end_date)
            
            for google_event in google_events:
                # Check if we already have this event locally
                existing = next((e for e in events if getattr(e, 'google_event_id', None) == google_event['google_event_id']), None)
                if not existing:
                    # Create local representation of Google event
                    event_dict = {
                        "_id": f"google_{google_event['google_event_id']}",
                        "user_id": user_id,
                        "title": google_event['title'],
                        "description": google_event['description'],
                        "start_time": google_event['start_time'],
                        "end_time": google_event['end_time'],
                        "location": google_event['location'],
                        "all_day": False,
                        "recurring": False,
                        "reminder_minutes": 15,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now(),
                        "google_event_id": google_event['google_event_id'],
                        "synced_to_google": True
                    }
                    events.append(CalendarEvent(**event_dict))
        
        # Sort all events by start time
        events.sort(key=lambda x: x.start_time)
        return events
    
    async def get_calendar_view(self, user_id: str, view_type: str = "week", start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get calendar view data grouped by time periods"""
        if not start_date:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if view_type == "day":
            end_date = start_date + timedelta(days=1)
        elif view_type == "week":
            # Start from Monday
            start_date = start_date - timedelta(days=start_date.weekday())
            end_date = start_date + timedelta(days=7)
        elif view_type == "month":
            # Start from first day of month
            start_date = start_date.replace(day=1)
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1)
        else:
            end_date = start_date + timedelta(days=7)  # Default to week
        
        events = await self.get_events(user_id, start_date, end_date)
        
        # Group events by date
        grouped_events = {}
        task_events = []
        focus_sessions = []
        
        for event in events:
            event_date = event.start_time.date()
            date_str = event_date.isoformat()
            
            if date_str not in grouped_events:
                grouped_events[date_str] = []
            
            event_data = {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "location": event.location,
                "all_day": event.all_day,
                "synced_to_google": getattr(event, 'synced_to_google', False)
            }
            
            grouped_events[date_str].append(event_data)
            
            # Categorize events
            if "🎯" in event.title:
                task_events.append(event_data)
            elif "Focus Session" in event.title:
                focus_sessions.append(event_data)
        
        return {
            "view_type": view_type,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "events_by_date": grouped_events,
            "total_events": len(events),
            "task_events": len(task_events),
            "focus_sessions": len(focus_sessions),
            "google_calendar_connected": await self.is_google_calendar_connected(user_id)
        }
    
    async def update_event(self, event_id: str, user_id: str, event_data: Dict[str, Any], sync_to_google: bool = True) -> Optional[CalendarEvent]:
        """Update a calendar event"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            event_data["updated_at"] = datetime.now()
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(event_id), "user_id": user_id},
                {"$set": event_data},
                return_document=True
            )
            
            if result:
                # Sync to Google Calendar if enabled and synced
                if sync_to_google and result.get('google_event_id') and result.get('synced_to_google'):
                    await self.google_calendar.update_event(user_id, result['google_event_id'], event_data)
                
                result["_id"] = str(result["_id"])
                return CalendarEvent(**result)
            return None
        except Exception as e:
            logger.error(f"Failed to update event: {e}")
            return None
    
    async def delete_event(self, event_id: str, user_id: str, sync_to_google: bool = True) -> bool:
        """Delete a calendar event"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Get event first for Google sync
            event = await self.collection.find_one({"_id": ObjectId(event_id), "user_id": user_id})
            
            if event and sync_to_google and event.get('google_event_id') and event.get('synced_to_google'):
                await self.google_calendar.delete_event(user_id, event['google_event_id'])
            
            result = await self.collection.delete_one(
                {"_id": ObjectId(event_id), "user_id": user_id}
            )
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            return False
    
    async def sync_with_google_calendar(self, user_id: str) -> Dict[str, Any]:
        """Sync local calendar with Google Calendar"""
        if not await self.is_google_calendar_connected(user_id):
            return {"success": False, "error": "Google Calendar not connected"}
        
        try:
            # Get events from last 30 days to next 90 days
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now() + timedelta(days=90)
            
            google_events = await self.google_calendar.get_events(user_id, start_date, end_date)
            synced_count = 0
            
            for google_event in google_events:
                # Check if event already exists locally
                existing = await self.collection.find_one({
                    "google_event_id": google_event['google_event_id'],
                    "user_id": user_id
                })
                
                if not existing:
                    # Create new local event
                    event_dict = {
                        "user_id": user_id,
                        "title": google_event['title'],
                        "description": google_event['description'],
                        "start_time": google_event['start_time'],
                        "end_time": google_event['end_time'],
                        "location": google_event['location'],
                        "all_day": False,
                        "recurring": False,
                        "reminder_minutes": 15,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now(),
                        "google_event_id": google_event['google_event_id'],
                        "synced_to_google": True
                    }
                    await self.collection.insert_one(event_dict)
                    synced_count += 1
            
            return {
                "success": True,
                "synced_events": synced_count,
                "message": f"Synced {synced_count} events from Google Calendar"
            }
        except Exception as e:
            logger.error(f"Failed to sync with Google Calendar: {e}")
            return {"success": False, "error": str(e)}

# Global calendar service instance
calendar_service = CalendarService()