"""
Performance monitoring and metrics tracking system.
Provides comprehensive monitoring of application performance and health.
"""

import time
import asyncio
import logging
from functools import wraps
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
import json
import psutil
import os

logger = logging.getLogger(__name__)

@dataclass
class RequestMetric:
    """Individual request metric"""
    endpoint: str
    duration: float
    status: str  # "success", "error", "timeout"
    timestamp: datetime
    user_id: Optional[str] = None
    request_size: Optional[int] = None
    response_size: Optional[int] = None
    error_type: Optional[str] = None

@dataclass
class EndpointStats:
    """Statistics for an endpoint"""
    count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    max_time: float = 0.0
    min_time: float = float('inf')
    success_count: int = 0
    error_count: int = 0
    p95_time: float = 0.0
    p99_time: float = 0.0
    recent_times: deque = field(default_factory=lambda: deque(maxlen=1000))

class PerformanceMonitor:
    """Comprehensive performance monitoring system"""
    
    def __init__(self, max_metrics: int = 10000):
        self.metrics = {}
        self.request_times = []
        self.max_metrics = max_metrics
        self.start_time = datetime.now()
        
        # System metrics
        self.system_metrics = {
            'cpu_percent': deque(maxlen=100),
            'memory_percent': deque(maxlen=100),
            'disk_usage': deque(maxlen=100),
            'network_io': deque(maxlen=100)
        }
        
        # Custom counters
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(lambda: deque(maxlen=1000))
        
        # Recent errors
        self.recent_errors = deque(maxlen=100)
        
        # Background task for system monitoring
        self._monitoring_task = None
        self._monitoring_active = False
    
    async def start_monitoring(self, interval: float = 30.0):
        """Start background system monitoring"""
        if not self._monitoring_active:
            self._monitoring_active = True
            self._monitoring_task = asyncio.create_task(
                self._system_monitoring_loop(interval)
            )
            logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring"""
        self._monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")
    
    def track_request_time(self, endpoint: str, duration: float, status: str = "success", 
                          user_id: Optional[str] = None, error_type: Optional[str] = None):
        """Track request timing and status"""
        if endpoint not in self.metrics:
            self.metrics[endpoint] = EndpointStats()
        
        metric = self.metrics[endpoint]
        metric.count += 1
        metric.total_time += duration
        metric.avg_time = metric.total_time / metric.count
        metric.max_time = max(metric.max_time, duration)
        metric.min_time = min(metric.min_time, duration)
        metric.recent_times.append(duration)
        
        if status == "success":
            metric.success_count += 1
        else:
            metric.error_count += 1
        
        # Calculate percentiles
        if len(metric.recent_times) > 10:
            sorted_times = sorted(metric.recent_times)
            metric.p95_time = sorted_times[int(len(sorted_times) * 0.95)]
            metric.p99_time = sorted_times[int(len(sorted_times) * 0.99)]
        
        # Track request metric
        request_metric = RequestMetric(
            endpoint=endpoint,
            duration=duration,
            status=status,
            timestamp=datetime.now(),
            user_id=user_id,
            error_type=error_type
        )
        
        # Log slow requests
        if duration > 5.0:
            logger.warning(f"Slow request: {endpoint} took {duration:.2f}s")
            
        # Log errors
        if status == "error":
            self.recent_errors.append({
                'endpoint': endpoint,
                'duration': duration,
                'error_type': error_type,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id
            })
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        key = self._make_metric_key(name, tags)
        self.counters[key] += value
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric"""
        key = self._make_metric_key(name, tags)
        self.gauges[key] = value
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a histogram value"""
        key = self._make_metric_key(name, tags)
        self.histograms[key].append(value)
    
    def _make_metric_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Create metric key with tags"""
        if not tags:
            return name
        tag_string = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_string}]"
    
    async def _system_monitoring_loop(self, interval: float):
        """Background loop for system metrics collection"""
        while self._monitoring_active:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.system_metrics['cpu_percent'].append(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.system_metrics['memory_percent'].append(memory.percent)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.system_metrics['disk_usage'].append(disk_percent)
                
                # Network I/O (simplified)
                net_io = psutil.net_io_counters()
                self.system_metrics['network_io'].append({
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'timestamp': time.time()
                })
                
                # Custom gauges for system metrics
                self.set_gauge('system.cpu_percent', cpu_percent)
                self.set_gauge('system.memory_percent', memory.percent)
                self.set_gauge('system.disk_percent', disk_percent)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                await asyncio.sleep(interval)
    
    def get_endpoint_stats(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for endpoints"""
        if endpoint:
            if endpoint in self.metrics:
                metric = self.metrics[endpoint]
                return {
                    'count': metric.count,
                    'avg_time': metric.avg_time,
                    'max_time': metric.max_time,
                    'min_time': metric.min_time if metric.min_time != float('inf') else 0,
                    'success_rate': metric.success_count / max(metric.count, 1),
                    'p95_time': metric.p95_time,
                    'p99_time': metric.p99_time
                }
            return {}
        
        # Return all endpoints
        result = {}
        for endpoint, metric in self.metrics.items():
            result[endpoint] = {
                'count': metric.count,
                'avg_time': metric.avg_time,
                'max_time': metric.max_time,
                'min_time': metric.min_time if metric.min_time != float('inf') else 0,
                'success_rate': metric.success_count / max(metric.count, 1),
                'p95_time': metric.p95_time,
                'p99_time': metric.p99_time
            }
        return result
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system performance statistics"""
        stats = {}
        
        for metric_name, values in self.system_metrics.items():
            if values:
                if metric_name == 'network_io':
                    # Special handling for network I/O
                    if len(values) >= 2:
                        latest = values[-1]
                        previous = values[-2]
                        time_diff = latest['timestamp'] - previous['timestamp']
                        if time_diff > 0:
                            bytes_sent_rate = (latest['bytes_sent'] - previous['bytes_sent']) / time_diff
                            bytes_recv_rate = (latest['bytes_recv'] - previous['bytes_recv']) / time_diff
                            stats[metric_name] = {
                                'bytes_sent_rate': bytes_sent_rate,
                                'bytes_recv_rate': bytes_recv_rate
                            }
                else:
                    # Regular metrics
                    numeric_values = [v for v in values if isinstance(v, (int, float))]
                    if numeric_values:
                        stats[metric_name] = {
                            'current': numeric_values[-1],
                            'avg': sum(numeric_values) / len(numeric_values),
                            'max': max(numeric_values),
                            'min': min(numeric_values)
                        }
        
        return stats
    
    def get_counters(self) -> Dict[str, int]:
        """Get all counter values"""
        return dict(self.counters)
    
    def get_gauges(self) -> Dict[str, float]:
        """Get all gauge values"""
        return dict(self.gauges)
    
    def get_histograms(self) -> Dict[str, Dict[str, float]]:
        """Get histogram statistics"""
        result = {}
        for name, values in self.histograms.items():
            if values:
                sorted_values = sorted(values)
                result[name] = {
                    'count': len(values),
                    'avg': sum(values) / len(values),
                    'max': max(values),
                    'min': min(values),
                    'p50': sorted_values[int(len(sorted_values) * 0.5)],
                    'p95': sorted_values[int(len(sorted_values) * 0.95)],
                    'p99': sorted_values[int(len(sorted_values) * 0.99)]
                }
        return result
    
    def get_recent_errors(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent errors"""
        return list(self.recent_errors)[-limit:]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        total_requests = sum(metric.count for metric in self.metrics.values())
        total_errors = sum(metric.error_count for metric in self.metrics.values())
        
        uptime = datetime.now() - self.start_time
        
        # System health indicators
        system_stats = self.get_system_stats()
        
        health_status = "healthy"
        if system_stats.get('cpu_percent', {}).get('current', 0) > 80:
            health_status = "warning"
        if system_stats.get('memory_percent', {}).get('current', 0) > 90:
            health_status = "critical"
        
        return {
            'status': health_status,
            'uptime_seconds': uptime.total_seconds(),
            'total_requests': total_requests,
            'total_errors': total_errors,
            'error_rate': total_errors / max(total_requests, 1),
            'system_stats': system_stats,
            'recent_error_count': len(self.recent_errors)
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.recent_errors.clear()
        for values in self.system_metrics.values():
            values.clear()
        self.start_time = datetime.now()
        logger.info("Performance monitoring stats reset")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Decorators for automatic monitoring
def monitor_performance(endpoint_name: Optional[str] = None, track_args: bool = False):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = endpoint_name or func.__name__
            start_time = time.time()
            status = "success"
            error_type = None
            
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                error_type = type(e).__name__
                raise
            finally:
                duration = time.time() - start_time
                
                # Extract user_id if available
                user_id = None
                if track_args and args:
                    # Look for user_id in common positions
                    for arg in args:
                        if isinstance(arg, str) and len(arg) == 24:  # MongoDB ObjectId length
                            user_id = arg
                            break
                
                performance_monitor.track_request_time(
                    name, duration, status, user_id, error_type
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = endpoint_name or func.__name__
            start_time = time.time()
            status = "success"
            error_type = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                error_type = type(e).__name__
                raise
            finally:
                duration = time.time() - start_time
                
                # Extract user_id if available
                user_id = None
                if track_args and args:
                    for arg in args:
                        if isinstance(arg, str) and len(arg) == 24:
                            user_id = arg
                            break
                
                performance_monitor.track_request_time(
                    name, duration, status, user_id, error_type
                )
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def track_counter(name: str, tags: Optional[Dict[str, str]] = None):
    """Decorator to increment counter on function calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            performance_monitor.increment_counter(name, tags=tags)
            return func(*args, **kwargs)
        return wrapper
    return decorator
