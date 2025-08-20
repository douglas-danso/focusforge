"""
Enhanced Calendar API endpoints for FocusForge
Provides comprehensive calendar management with Google Calendar integration
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks, Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.services.calendar_service import CalendarService
from app.models.schemas import CalendarEvent, CalendarEventCreate
from app.models.api_schemas import validate_user_id
from app.core.database import get_database
from app.core.auth import get_current_user_from_token

router = APIRouter()

# ===== GOOGLE CALENDAR INTEGRATION =====

@router.get("/google/auth-url")
async def get_google_auth_url(
    user_id: str = Depends(get_current_user_from_token)
):
    """Get Google Calendar authorization URL"""
    try:
        user_id = validate_user_id(user_id)
        calendar_service = CalendarService()
        auth_url = await calendar_service.get_google_auth_url(user_id)
        
        return {
            "success": True,
            "auth_url": auth_url,
            "message": "Please visit the URL to authorize Google Calendar access",
            "instructions": [
                "1. Click the authorization URL",
                "2. Sign in to your Google account",
                "3. Grant calendar permissions",
                "4. Copy the authorization code",
                "5. Use the code with /calendar/google/authorize endpoint"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get auth URL: {str(e)}")

@router.post("/google/authorize")
async def authorize_google_calendar(
    authorization_code: str = Query(..., description="Authorization code from Google"),
    user_id: str = Depends(get_current_user_from_token)
):
    """Authorize Google Calendar integration"""
    try:
        user_id = validate_user_id(user_id)
        calendar_service = CalendarService()
        success = await calendar_service.authorize_google_calendar(user_id, authorization_code)
        
        if success:
            return {
                "success": True,
                "message": "Google Calendar successfully connected!",
                "features_enabled": [
                    "Automatic task scheduling to Google Calendar",
                    "Two-way sync with Google Calendar",
                    "Task block calendar events",
                    "Focus session scheduling"
                ]
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to authorize Google Calendar")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authorization failed: {str(e)}")

@router.get("/google/status")
async def get_google_calendar_status(
    user_id: str = Depends(get_current_user_from_token)
):
    """Check Google Calendar connection status"""
    try:
        user_id = validate_user_id(user_id)
        calendar_service = CalendarService()
        connected = await calendar_service.is_google_calendar_connected(user_id)
        
        return {
            "connected": connected,
            "user_id": user_id,
            "status": "connected" if connected else "not_connected",
            "message": "Google Calendar is connected" if connected else "Google Calendar is not connected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check status: {str(e)}")

@router.post("/google/sync")
async def sync_google_calendar(
    user_id: str = Depends(get_current_user_from_token),
    background_tasks: BackgroundTasks = None
):
    """Sync with Google Calendar"""
    try:
        user_id = validate_user_id(user_id)
        calendar_service = CalendarService()
        
        if background_tasks:
            background_tasks.add_task(calendar_service.sync_with_google_calendar, user_id)
            return {
                "success": True,
                "message": "Google Calendar sync started in background",
                "sync_mode": "background"
            }
        else:
            result = await calendar_service.sync_with_google_calendar(user_id)
            return {
                **result,
                "sync_mode": "immediate"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

# ===== CALENDAR EVENT MANAGEMENT =====

@router.post("/events", response_model=Dict[str, Any])
async def create_calendar_event(
    event_data: CalendarEventCreate,
    user_id: str = Depends(get_current_user_from_token),
    sync_to_google: bool = Query(True, description="Sync to Google Calendar"),
    db=Depends(get_database)
):
    """Create a new calendar event"""
    try:
        user_id = validate_user_id(user_id)
        calendar_service = CalendarService(db)
        event = await calendar_service.create_event(user_id, event_data, sync_to_google)
        
        return {
            "success": True,
            "event": {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "location": event.location,
                "all_day": event.all_day,
                "recurring": event.recurring,
                "reminder_minutes": event.reminder_minutes,
                "synced_to_google": getattr(event, 'synced_to_google', False),
                "created_at": event.created_at.isoformat()
            },
            "google_sync": sync_to_google and getattr(event, 'synced_to_google', False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@router.post("/tasks/{task_id}/calendar-events")
async def create_task_calendar_events(
    task_id: str = Path(..., description="Task ID"),
    task_title: str = Query(..., description="Task title"),
    user_id: str = Depends(get_current_user_from_token),
    spacing_hours: int = Query(1, description="Hours between task blocks"),
    start_time: Optional[str] = Query(None, description="Start time for first block (ISO format)"),
    db=Depends(get_database)
):
    """Create calendar events for task blocks with intelligent scheduling"""
    try:
        user_id = validate_user_id(user_id)
        calendar_service = CalendarService(db)
        
        # Get task blocks
        blocks_cursor = db.task_blocks.find({"task_id": task_id})
        blocks = []
        async for block in blocks_cursor:
            block["_id"] = str(block["_id"])
            blocks.append(block)
        
        if not blocks:
            raise HTTPException(status_code=404, detail="No task blocks found for this task")
        
        # Calculate optimal start time if not provided
        if start_time:
            base_start_time = datetime.fromisoformat(start_time)
        else:
            # Default to next available time slot
            base_start_time = datetime.now() + timedelta(hours=1)
            base_start_time = base_start_time.replace(minute=0, second=0, microsecond=0)
        
        events = []
        current_time = base_start_time
        
        for i, block in enumerate(blocks):
            # Create event for this block
            event_data = CalendarEventCreate(
                title=f"🎯 {task_title} - Block {i+1}: {block.get('title', f'Task Block {i+1}')}",
                description=f"""Task Block {i+1} of {len(blocks)}

📋 Block Details:
{block.get('description', 'Focus on task completion')}

⏱️ Estimated Duration: {block.get('duration_minutes', 25)} minutes
🎯 Task: {task_title}
🔗 Task ID: {task_id}

💡 Focus Tips:
- Remove distractions from workspace
- Have water and snacks ready
- Use Pomodoro technique if needed
- Take breaks between blocks""",
                start_time=current_time,
                end_time=current_time + timedelta(minutes=block.get('duration_minutes', 25)),
                location="Focus Zone 🧘‍♂️",
                all_day=False,
                recurring=False,
                reminder_minutes=5
            )
            
            event = await calendar_service.create_event(user_id, event_data)
            
            # Link event to task block
            await db.task_blocks.update_one(
                {"_id": block["_id"]},
                {"$set": {
                    "calendar_event_id": event.id,
                    "scheduled_start": current_time,
                    "scheduled_end": current_time + timedelta(minutes=block.get('duration_minutes', 25))
                }}
            )
            
            events.append(event)
            
            # Calculate next block start time
            current_time += timedelta(
                minutes=block.get('duration_minutes', 25) + 
                block.get('break_minutes', 5) + 
                (spacing_hours * 60)
            )
        
        return {
            "success": True,
            "task_id": task_id,
            "task_title": task_title,
            "created_events": len(events),
            "total_duration_hours": round((current_time - base_start_time).total_seconds() / 3600, 2),
            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat(),
                    "duration_minutes": (event.end_time - event.start_time).total_seconds() / 60,
                    "synced_to_google": getattr(event, 'synced_to_google', False)
                }
                for event in events
            ],
            "scheduling_info": {
                "first_block_start": base_start_time.isoformat(),
                "last_block_end": (current_time - timedelta(hours=spacing_hours)).isoformat(),
                "spacing_hours": spacing_hours
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task events: {str(e)}")

@router.get("/events", response_model=List[Dict[str, Any]])
async def get_calendar_events(
    user_id: str = Depends(get_current_user_from_token),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    include_google: bool = Query(True, description="Include Google Calendar events"),
    event_type: Optional[str] = Query(None, description="Filter by event type (task/focus/meeting)"),
    db=Depends(get_database)
):
    """Get calendar events for a user with advanced filtering"""
    try:
        user_id = validate_user_id(user_id)
        calendar_service = CalendarService(db)
        
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        events = await calendar_service.get_events(user_id, start_dt, end_dt, include_google)
        
        # Filter by event type if specified
        if event_type:
            filtered_events = []
            for event in events:
                if event_type == "task" and "🎯" in event.title:
                    filtered_events.append(event)
                elif event_type == "focus" and "Focus Session" in event.title:
                    filtered_events.append(event)
                elif event_type == "meeting" and "🎯" not in event.title and "Focus Session" not in event.title:
                    filtered_events.append(event)
                elif event_type == "all":
                    filtered_events.append(event)
            events = filtered_events
        
        return [
            {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "duration_minutes": round((event.end_time - event.start_time).total_seconds() / 60),
                "location": event.location,
                "all_day": event.all_day,
                "recurring": event.recurring,
                "reminder_minutes": event.reminder_minutes,
                "synced_to_google": getattr(event, 'synced_to_google', False),
                "event_type": (
                    "task" if "🎯" in event.title else
                    "focus" if "Focus Session" in event.title else
                    "meeting"
                ),
                "created_at": event.created_at.isoformat()
            }
            for event in events
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")

@router.get("/view/{view_type}")
async def get_calendar_view(
    view_type: str = Path(..., description="View type: day, week, month"),
    user_id: str = Depends(get_current_user_from_token),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    include_stats: bool = Query(True, description="Include productivity statistics"),
    db=Depends(get_database)
):
    """Get calendar view with productivity insights"""
    try:
        user_id = validate_user_id(user_id)
        
        if view_type not in ["day", "week", "month"]:
            raise HTTPException(status_code=400, detail="view_type must be 'day', 'week', or 'month'")
        
        calendar_service = CalendarService(db)
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        view_data = await calendar_service.get_calendar_view(user_id, view_type, start_dt)
        
        # Add productivity insights if requested
        if include_stats:
            total_focus_time = 0
            total_task_blocks = 0
            completed_tasks = 0
            
            for date_events in view_data["events_by_date"].values():
                for event in date_events:
                    if "🎯" in event["title"]:
                        total_task_blocks += 1
                        if event.get("completed", False):
                            completed_tasks += 1
                    
                    # Calculate focus time (task events + focus sessions)
                    if "🎯" in event["title"] or "Focus Session" in event["title"]:
                        start = datetime.fromisoformat(event["start_time"])
                        end = datetime.fromisoformat(event["end_time"])
                        total_focus_time += (end - start).total_seconds() / 60
            
            view_data["productivity_stats"] = {
                "total_focus_minutes": round(total_focus_time),
                "total_focus_hours": round(total_focus_time / 60, 2),
                "total_task_blocks": total_task_blocks,
                "completed_tasks": completed_tasks,
                "completion_rate": round((completed_tasks / total_task_blocks * 100) if total_task_blocks > 0 else 0, 1),
                "avg_daily_focus_hours": round(total_focus_time / 60 / max(len(view_data["events_by_date"]), 1), 2)
            }
        
        return view_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get calendar view: {str(e)}")

@router.put("/events/{event_id}")
async def update_calendar_event(
    event_id: str = Path(..., description="Event ID"),
    updates: Dict[str, Any] = None,
    user_id: str = Depends(get_current_user_from_token),
    sync_to_google: bool = Query(True, description="Sync to Google Calendar"),
    db=Depends(get_database)
):
    """Update a calendar event"""
    try:
        user_id = validate_user_id(user_id)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        calendar_service = CalendarService(db)
        event = await calendar_service.update_event(event_id, user_id, updates, sync_to_google)
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {
            "success": True,
            "event": {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "location": event.location,
                "synced_to_google": getattr(event, 'synced_to_google', False),
                "updated_at": event.updated_at.isoformat()
            },
            "updated_fields": list(updates.keys())
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")

@router.delete("/events/{event_id}")
async def delete_calendar_event(
    event_id: str = Path(..., description="Event ID"),
    user_id: str = Depends(get_current_user_from_token),
    sync_to_google: bool = Query(True, description="Sync to Google Calendar"),
    db=Depends(get_database)
):
    """Delete a calendar event"""
    try:
        user_id = validate_user_id(user_id)
        calendar_service = CalendarService(db)
        success = await calendar_service.delete_event(event_id, user_id, sync_to_google)
        
        if not success:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {
            "success": True,
            "message": "Event deleted successfully",
            "event_id": event_id,
            "google_sync": sync_to_google
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")

# ===== CALENDAR UTILITIES =====

@router.get("/upcoming")
async def get_upcoming_events(
    user_id: str = Depends(get_current_user_from_token),
    hours: int = Query(24, description="Hours ahead to look"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    db=Depends(get_database)
):
    """Get upcoming events with smart filtering"""
    try:
        user_id = validate_user_id(user_id)
        calendar_service = CalendarService(db)
        
        now = datetime.now()
        events = await calendar_service.get_events(
            user_id, 
            now, 
            now + timedelta(hours=hours)
        )
        
        # Filter by event type if specified
        if event_type:
            if event_type == "task":
                events = [e for e in events if "🎯" in e.title]
            elif event_type == "focus":
                events = [e for e in events if "Focus Session" in e.title]
        
        return {
            "success": True,
            "user_id": user_id,
            "time_range_hours": hours,
            "event_type_filter": event_type,
            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat(),
                    "location": event.location,
                    "time_until_start": str(event.start_time - now),
                    "synced_to_google": getattr(event, 'synced_to_google', False)
                }
                for event in events
            ],
            "total_events": len(events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get upcoming events: {str(e)}")

@router.post("/availability/check")
async def check_time_availability(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)"),
    user_id: str = Depends(get_current_user_from_token),
    buffer_minutes: int = Query(15, description="Buffer time in minutes"),
    db=Depends(get_database)
):
    """Check if a time slot is available with smart conflict detection"""
    try:
        user_id = validate_user_id(user_id)
        calendar_service = CalendarService(db)
        
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        
        # Add buffer time
        buffered_start = start_dt - timedelta(minutes=buffer_minutes)
        buffered_end = end_dt + timedelta(minutes=buffer_minutes)
        
        # Get events in the time range
        events = await calendar_service.get_events(user_id, buffered_start, buffered_end)
        conflicts = []
        
        for event in events:
            if (event.start_time < end_dt and event.end_time > start_dt):
                conflicts.append({
                    "id": event.id,
                    "title": event.title,
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat(),
                    "conflict_type": "overlap"
                })
        
        is_available = len(conflicts) == 0
        
        return {
            "available": is_available,
            "requested_start": start_time,
            "requested_end": end_time,
            "duration_minutes": (end_dt - start_dt).total_seconds() / 60,
            "buffer_minutes": buffer_minutes,
            "conflicts": conflicts,
            "conflict_count": len(conflicts),
            "recommendation": (
                "Time slot is available" if is_available else
                f"Found {len(conflicts)} conflicting events. Consider rescheduling."
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check availability: {str(e)}")

@router.get("/insights/productivity")
async def get_productivity_insights(
    user_id: str = Depends(get_current_user_from_token),
    days_back: int = Query(7, description="Number of days to analyze"),
    db=Depends(get_database)
):
    """Get productivity insights from calendar data"""
    try:
        user_id = validate_user_id(user_id)
        calendar_service = CalendarService(db)
        
        # Get events from the specified period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        events = await calendar_service.get_events(user_id, start_date, end_date)
        
        # Analyze productivity patterns
        daily_stats = {}
        total_focus_time = 0
        total_task_blocks = 0
        peak_hours = {}
        
        for event in events:
            date_key = event.start_time.date().isoformat()
            hour_key = event.start_time.hour
            
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    "focus_minutes": 0,
                    "task_blocks": 0,
                    "meetings": 0
                }
            
            duration_minutes = (event.end_time - event.start_time).total_seconds() / 60
            
            if "🎯" in event.title or "Focus Session" in event.title:
                daily_stats[date_key]["focus_minutes"] += duration_minutes
                total_focus_time += duration_minutes
                
                if "🎯" in event.title:
                    daily_stats[date_key]["task_blocks"] += 1
                    total_task_blocks += 1
                
                # Track peak hours
                peak_hours[hour_key] = peak_hours.get(hour_key, 0) + duration_minutes
            else:
                daily_stats[date_key]["meetings"] += 1
        
        # Find most productive hour
        most_productive_hour = max(peak_hours.items(), key=lambda x: x[1])[0] if peak_hours else 9
        
        # Calculate trends
        avg_daily_focus = total_focus_time / max(days_back, 1)
        avg_daily_tasks = total_task_blocks / max(days_back, 1)
        
        return {
            "success": True,
            "user_id": user_id,
            "analysis_period": {
                "days": days_back,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_focus_hours": round(total_focus_time / 60, 2),
                "total_task_blocks": total_task_blocks,
                "avg_daily_focus_hours": round(avg_daily_focus / 60, 2),
                "avg_daily_task_blocks": round(avg_daily_tasks, 1),
                "most_productive_hour": most_productive_hour,
                "productivity_score": min(100, round((total_focus_time / (days_back * 8 * 60)) * 100, 1))
            },
            "daily_breakdown": daily_stats,
            "recommendations": [
                f"Your most productive hour is {most_productive_hour}:00. Schedule important tasks then.",
                f"You average {round(avg_daily_focus / 60, 1)} hours of focus time daily.",
                "Consider blocking more time for deep work if productivity score is below 70%."
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get productivity insights: {str(e)}")