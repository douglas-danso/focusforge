"""
Background task system using RQ (Redis Queue)
Handles long-running operations and scheduled tasks
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from functools import wraps

import redis
from rq import Queue, Worker, Connection
from rq.job import Job
from rq_scheduler import Scheduler

from app.core.orchestrator import mcp_orchestrator
from app.core.planner import action_planner
from app.core.memory import memory_manager
from app.core.unified_mcp import unified_mcp
from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis connection
try:
    redis_conn = redis.Redis(host='redis-master', port=6379, db=0, decode_responses=True)
    redis_conn.ping()  # Test connection
except Exception as e:
    logger.warning(f"Redis not available, using in-memory fallback: {e}")
    redis_conn = None

# RQ setup
if redis_conn:
    task_queue = Queue('focusforge_tasks', connection=redis_conn)
    scheduler = Scheduler(connection=redis_conn)
else:
    task_queue = None
    scheduler = None


def async_task(func):
    """Decorator to convert async functions for RQ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


class BackgroundTaskManager:
    """
    Manages background tasks and scheduled operations
    """
    
    def __init__(self):
        self.redis_conn = redis_conn
        self.task_queue = task_queue
        self.scheduler = scheduler
        self.fallback_tasks = []  # For when Redis is not available
        self.running = False
    
    def is_available(self) -> bool:
        """Check if background task system is available"""
        return self.redis_conn is not None
    
    # ===== TASK ENQUEUING =====
    
    def enqueue_task(self, func, *args, **kwargs) -> Optional[str]:
        """Enqueue a background task"""
        if not self.is_available():
            # Fallback to immediate execution
            logger.warning("Redis not available, executing task immediately")
            try:
                func(*args, **kwargs)
                return "immediate_execution"
            except Exception as e:
                logger.error(f"Immediate task execution failed: {e}")
                return None
        
        try:
            job = self.task_queue.enqueue(func, *args, **kwargs)
            logger.info(f"Task enqueued: {job.id}")
            return job.id
        except Exception as e:
            logger.error(f"Failed to enqueue task: {e}")
            return None
    
    def enqueue_delayed_task(self, delay_seconds: int, func, *args, **kwargs) -> Optional[str]:
        """Enqueue a delayed task"""
        if not self.is_available():
            logger.warning("Redis not available, cannot schedule delayed task")
            return None
        
        try:
            job = self.task_queue.enqueue_in(
                timedelta(seconds=delay_seconds),
                func, 
                *args, 
                **kwargs
            )
            logger.info(f"Delayed task enqueued: {job.id}, delay: {delay_seconds}s")
            return job.id
        except Exception as e:
            logger.error(f"Failed to enqueue delayed task: {e}")
            return None
    
    def schedule_recurring_task(self, cron_string: str, func, *args, **kwargs) -> Optional[str]:
        """Schedule a recurring task using cron syntax"""
        if not self.is_available() or not self.scheduler:
            logger.warning("Scheduler not available")
            return None
        
        try:
            job = self.scheduler.cron(
                cron_string=cron_string,
                func=func,
                args=args,
                kwargs=kwargs
            )
            logger.info(f"Recurring task scheduled: {job.id}, cron: {cron_string}")
            return job.id
        except Exception as e:
            logger.error(f"Failed to schedule recurring task: {e}")
            return None
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a background job"""
        if not self.is_available():
            return None
        
        try:
            job = Job.fetch(job_id, connection=self.redis_conn)
            return {
                "id": job.id,
                "status": job.get_status(),
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "ended_at": job.ended_at.isoformat() if job.ended_at else None,
                "result": job.result,
                "exc_info": job.exc_info
            }
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return None
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a background job"""
        if not self.is_available():
            return False
        
        try:
            job = Job.fetch(job_id, connection=self.redis_conn)
            job.cancel()
            logger.info(f"Job cancelled: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel job: {e}")
            return False


# ===== BACKGROUND TASK FUNCTIONS =====

@async_task
async def process_task_creation_workflow(user_id: str, task_data: Dict[str, Any]):
    """Background processing of task creation workflow"""
    logger.info(f"Processing task creation workflow for user {user_id}")
    
    try:
        result = await mcp_orchestrator.handle_task_creation(user_id, task_data)
        
        # Store result for later retrieval
        await memory_manager.memory_store.store_memory(
            "working",
            f"bg_task_creation:{user_id}:{datetime.now().timestamp()}",
            result,
            user_id
        )
        
        logger.info(f"Task creation workflow completed for user {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Task creation workflow failed for user {user_id}: {e}")
        raise


@async_task
async def process_task_completion_workflow(user_id: str, completion_data: Dict[str, Any]):
    """Background processing of task completion workflow"""
    logger.info(f"Processing task completion workflow for user {user_id}")
    
    try:
        result = await mcp_orchestrator.handle_task_completion(user_id, completion_data)
        
        # Store result
        await memory_manager.memory_store.store_memory(
            "working",
            f"bg_task_completion:{user_id}:{datetime.now().timestamp()}",
            result,
            user_id
        )
        
        logger.info(f"Task completion workflow completed for user {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Task completion workflow failed for user {user_id}: {e}")
        raise


@async_task
async def process_daily_optimization(user_id: str, optimization_data: Dict[str, Any]):
    """Background processing of daily optimization"""
    logger.info(f"Processing daily optimization for user {user_id}")
    
    try:
        result = await mcp_orchestrator.handle_daily_optimization(user_id, optimization_data)
        
        # Store result
        await memory_manager.memory_store.store_memory(
            "working",
            f"bg_daily_optimization:{user_id}:{datetime.now().timestamp()}",
            result,
            user_id
        )
        
        logger.info(f"Daily optimization completed for user {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Daily optimization failed for user {user_id}: {e}")
        raise


@async_task
async def execute_planned_actions(user_id: str = None, max_actions: int = 10):
    """Background execution of planned actions"""
    logger.info(f"Executing planned actions for user {user_id or 'all users'}")
    
    try:
        executed_actions = await action_planner.execute_ready_actions(user_id, max_actions)
        
        logger.info(f"Executed {len(executed_actions)} planned actions")
        return {
            "executed_count": len(executed_actions),
            "actions": executed_actions
        }
        
    except Exception as e:
        logger.error(f"Action execution failed: {e}")
        raise


@async_task
async def cleanup_old_data():
    """Background cleanup of old data"""
    logger.info("Running data cleanup")
    
    try:
        # Clean up memory
        await memory_manager.cleanup_all_memories()
        
        # Clean up old actions
        await action_planner.cleanup_completed_actions(older_than_hours=48)
        
        logger.info("Data cleanup completed")
        return {"success": True, "cleaned_at": datetime.now().isoformat()}
        
    except Exception as e:
        logger.error(f"Data cleanup failed: {e}")
        raise


@async_task
async def send_user_reminders():
    """Background task to send user reminders"""
    logger.info("Sending user reminders")
    
    try:
        # This would typically query for users who need reminders
        # For now, it's a placeholder
        
        logger.info("User reminders sent")
        return {"reminders_sent": 0}
        
    except Exception as e:
        logger.error(f"Reminder sending failed: {e}")
        raise


@async_task
async def sync_calendar_events(user_id: str):
    """Background calendar synchronization"""
    logger.info(f"Syncing calendar for user {user_id}")
    
    try:
        # Use MCP to sync calendar
        result = await unified_mcp.call_tool(
            "add_calendar_event",
            {
                "user_id": user_id,
                "title": "FocusForge Sync",
                "start_time": datetime.now().isoformat(),
                "end_time": (datetime.now() + timedelta(minutes=1)).isoformat(),
                "metadata": {"sync": True}
            }
        )
        
        logger.info(f"Calendar sync completed for user {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Calendar sync failed for user {user_id}: {e}")
        raise


@async_task
async def analyze_user_patterns(user_id: str):
    """Background analysis of user patterns"""
    logger.info(f"Analyzing patterns for user {user_id}")
    
    try:
        # Get user's recent activities from memory
        recent_actions = await memory_manager.memory_store.search_memories(
            "working",
            {"user_id": user_id},
            user_id,
            limit=50
        )
        
        # Simple pattern analysis (can be enhanced with ML)
        patterns = {
            "activity_level": len(recent_actions),
            "most_active_time": "morning",  # Placeholder
            "preferred_task_duration": 30,  # Placeholder
            "completion_rate": 0.8,  # Placeholder
            "analysis_date": datetime.now().isoformat()
        }
        
        # Store patterns in long-term memory
        await memory_manager.memory_store.store_memory(
            "long_term",
            f"user_patterns:{user_id}",
            patterns,
            user_id
        )
        
        logger.info(f"Pattern analysis completed for user {user_id}")
        return patterns
        
    except Exception as e:
        logger.error(f"Pattern analysis failed for user {user_id}: {e}")
        raise


# ===== TASK MANAGER INTEGRATION =====

class TaskScheduler:
    """
    High-level interface for scheduling background tasks
    """
    
    def __init__(self):
        self.task_manager = BackgroundTaskManager()
    
    def schedule_task_creation(self, user_id: str, task_data: Dict[str, Any], delay_seconds: int = 0) -> Optional[str]:
        """Schedule task creation workflow"""
        if delay_seconds > 0:
            return self.task_manager.enqueue_delayed_task(
                delay_seconds,
                process_task_creation_workflow,
                user_id,
                task_data
            )
        else:
            return self.task_manager.enqueue_task(
                process_task_creation_workflow,
                user_id,
                task_data
            )
    
    def schedule_task_completion(self, user_id: str, completion_data: Dict[str, Any]) -> Optional[str]:
        """Schedule task completion workflow"""
        return self.task_manager.enqueue_task(
            process_task_completion_workflow,
            user_id,
            completion_data
        )
    
    def schedule_daily_optimization(self, user_id: str, optimization_data: Dict[str, Any]) -> Optional[str]:
        """Schedule daily optimization"""
        return self.task_manager.enqueue_task(
            process_daily_optimization,
            user_id,
            optimization_data
        )
    
    def schedule_action_execution(self, user_id: str = None, delay_seconds: int = 0) -> Optional[str]:
        """Schedule action execution"""
        if delay_seconds > 0:
            return self.task_manager.enqueue_delayed_task(
                delay_seconds,
                execute_planned_actions,
                user_id
            )
        else:
            return self.task_manager.enqueue_task(execute_planned_actions, user_id)
    
    def setup_recurring_tasks(self):
        """Set up recurring background tasks"""
        if not self.task_manager.is_available():
            logger.warning("Cannot set up recurring tasks - Redis not available")
            return
        
        # Clean up old data every 6 hours
        self.task_manager.schedule_recurring_task(
            "0 */6 * * *",  # Every 6 hours
            cleanup_old_data
        )
        
        # Execute pending actions every 5 minutes
        self.task_manager.schedule_recurring_task(
            "*/5 * * * *",  # Every 5 minutes
            execute_planned_actions
        )
        
        # Send reminders every hour
        self.task_manager.schedule_recurring_task(
            "0 * * * *",  # Every hour
            send_user_reminders
        )
        
        logger.info("Recurring tasks set up successfully")
    
    def get_task_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a background task"""
        return self.task_manager.get_job_status(job_id)
    
    def cancel_task(self, job_id: str) -> bool:
        """Cancel a background task"""
        return self.task_manager.cancel_job(job_id)


# ===== WORKER MANAGEMENT =====

def start_worker():
    """Start an RQ worker"""
    if not redis_conn:
        logger.error("Cannot start worker - Redis not available")
        return
    
    with Connection(redis_conn):
        worker = Worker(['focusforge_tasks'])
        logger.info("Starting RQ worker...")
        worker.work()


def start_scheduler():
    """Start the RQ scheduler"""
    if not redis_conn or not scheduler:
        logger.error("Cannot start scheduler - Redis or scheduler not available")
        return
    
    logger.info("Starting RQ scheduler...")
    scheduler.run()


# Global instances
task_scheduler = TaskScheduler()

# Initialize recurring tasks if Redis is available
if redis_conn:
    try:
        task_scheduler.setup_recurring_tasks()
    except Exception as e:
        logger.warning(f"Failed to set up recurring tasks: {e}")
