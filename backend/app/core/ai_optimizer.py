"""
AI Request Optimizer with batching, rate limiting, and circuit breaker pattern.
Optimizes AI service calls for better performance and reliability.
"""

import asyncio
import time
import logging
from collections import deque
from typing import List, Dict, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit breaker is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service is back

@dataclass
class AIRequest:
    """Represents an AI request for batching"""
    func: Callable
    args: tuple
    kwargs: dict
    priority: int = 1  # 1 = low, 5 = high
    timeout: float = 30.0
    retries: int = 1
    request_id: str = ""

@dataclass
class RequestResult:
    """Result of an AI request"""
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    duration: float = 0.0
    retries_used: int = 0

class AIRequestOptimizer:
    """Optimize AI requests with batching, rate limiting, and circuit breaker"""
    
    def __init__(self, 
                 rate_limit: int = 10,  # requests per minute
                 circuit_breaker_threshold: int = 5,
                 circuit_breaker_timeout: int = 300,  # 5 minutes
                 max_concurrent: int = 3,
                 batch_size: int = 5,
                 batch_timeout: float = 1.0):
        
        # Rate limiting
        self.rate_limit = rate_limit
        self.request_times = deque()
        
        # Circuit breaker
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self.circuit_breaker_last_failure = None
        self.circuit_breaker_state = CircuitBreakerState.CLOSED
        
        # Concurrency control
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Batching
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.request_queue = asyncio.Queue()
        self.batch_processor_running = False
        
        # Metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.circuit_breaker_trips = 0
        self.rate_limited_requests = 0
        
        # Background task for batch processing
        self._batch_processor_task = None
        
    async def initialize(self):
        """Initialize the optimizer and start background tasks"""
        if not self.batch_processor_running:
            self._batch_processor_task = asyncio.create_task(self._batch_processor())
            self.batch_processor_running = True
            logger.info("AI Request Optimizer initialized")
    
    async def execute_ai_request(self, request_func: Callable, *args, **kwargs) -> Any:
        """Execute single AI request with optimizations"""
        request = AIRequest(
            func=request_func,
            args=args,
            kwargs=kwargs,
            request_id=f"req_{int(time.time() * 1000)}"
        )
        
        result = await self._process_single_request(request)
        
        if result.success:
            return result.result
        else:
            raise result.error
    
    async def execute_parallel_ai_requests(self, requests: List[Dict[str, Any]]) -> List[Any]:
        """Execute multiple AI requests in parallel with proper throttling"""
        ai_requests = []
        
        for i, req in enumerate(requests):
            ai_request = AIRequest(
                func=req['func'],
                args=req.get('args', ()),
                kwargs=req.get('kwargs', {}),
                priority=req.get('priority', 1),
                timeout=req.get('timeout', 30.0),
                retries=req.get('retries', 1),
                request_id=f"parallel_{i}_{int(time.time() * 1000)}"
            )
            ai_requests.append(ai_request)
        
        # Process requests with proper throttling
        tasks = [self._process_single_request(req) for req in ai_requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert results back to expected format
        processed_results = []
        for result in results:
            if isinstance(result, RequestResult):
                if result.success:
                    processed_results.append(result.result)
                else:
                    processed_results.append(result.error)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def execute_batch_requests(self, requests: List[AIRequest]) -> List[RequestResult]:
        """Execute requests as a batch (for similar operations)"""
        # Add requests to batch queue
        for request in requests:
            await self.request_queue.put(request)
        
        # Wait for processing (simplified - in production you'd want proper result tracking)
        await asyncio.sleep(self.batch_timeout * 2)
        
        # For now, return individual processing (batching logic can be enhanced)
        tasks = [self._process_single_request(req) for req in requests]
        return await asyncio.gather(*tasks)
    
    async def _process_single_request(self, request: AIRequest) -> RequestResult:
        """Process a single AI request with all optimizations"""
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # Circuit breaker check
            if self._is_circuit_open():
                self.circuit_breaker_trips += 1
                raise Exception(f"AI service circuit breaker is {self.circuit_breaker_state.value}")
            
            # Rate limiting
            await self._enforce_rate_limit()
            
            # Concurrency control
            async with self.semaphore:
                # Execute with retries
                for attempt in range(request.retries + 1):
                    try:
                        # Execute the actual request
                        if asyncio.iscoroutinefunction(request.func):
                            result = await asyncio.wait_for(
                                request.func(*request.args, **request.kwargs),
                                timeout=request.timeout
                            )
                        else:
                            result = request.func(*request.args, **request.kwargs)
                        
                        # Success - reset circuit breaker
                        self._reset_circuit_breaker()
                        self.successful_requests += 1
                        
                        duration = time.time() - start_time
                        return RequestResult(
                            success=True,
                            result=result,
                            duration=duration,
                            retries_used=attempt
                        )
                        
                    except asyncio.TimeoutError as e:
                        logger.warning(f"AI request timeout (attempt {attempt + 1}): {request.request_id}")
                        if attempt == request.retries:
                            raise e
                        await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                        
                    except Exception as e:
                        logger.warning(f"AI request failed (attempt {attempt + 1}): {e}")
                        if attempt == request.retries:
                            raise e
                        await asyncio.sleep(0.5 * (attempt + 1))
                
        except Exception as e:
            self._record_failure()
            self.failed_requests += 1
            duration = time.time() - start_time
            
            return RequestResult(
                success=False,
                error=e,
                duration=duration,
                retries_used=request.retries
            )
    
    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self.circuit_breaker_state == CircuitBreakerState.CLOSED:
            return False
        
        if self.circuit_breaker_state == CircuitBreakerState.OPEN:
            # Check if timeout has passed
            if (self.circuit_breaker_last_failure and 
                time.time() - self.circuit_breaker_last_failure > self.circuit_breaker_timeout):
                self.circuit_breaker_state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker moved to HALF_OPEN state")
                return False
            return True
        
        # HALF_OPEN state - allow one request through
        return False
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting"""
        now = time.time()
        
        # Remove old requests outside the window
        while self.request_times and now - self.request_times[0] > 60:
            self.request_times.popleft()
        
        # Check if we're at the limit
        if len(self.request_times) >= self.rate_limit:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                self.rate_limited_requests += 1
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
        
        self.request_times.append(now)
    
    def _record_failure(self):
        """Record a failure for circuit breaker"""
        self.circuit_breaker_failures += 1
        self.circuit_breaker_last_failure = time.time()
        
        # Check if we should open the circuit breaker
        if (self.circuit_breaker_failures >= self.circuit_breaker_threshold and 
            self.circuit_breaker_state == CircuitBreakerState.CLOSED):
            self.circuit_breaker_state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker OPENED after {self.circuit_breaker_failures} failures")
        elif self.circuit_breaker_state == CircuitBreakerState.HALF_OPEN:
            # Failed in half-open, go back to open
            self.circuit_breaker_state = CircuitBreakerState.OPEN
            logger.warning("Circuit breaker back to OPEN state after half-open failure")
    
    def _reset_circuit_breaker(self):
        """Reset circuit breaker on successful request"""
        if self.circuit_breaker_state != CircuitBreakerState.CLOSED:
            logger.info("Circuit breaker CLOSED - service recovered")
            
        self.circuit_breaker_failures = 0
        self.circuit_breaker_last_failure = None
        self.circuit_breaker_state = CircuitBreakerState.CLOSED
    
    async def _batch_processor(self):
        """Background task to process batched requests"""
        logger.info("AI batch processor started")
        
        while self.batch_processor_running:
            try:
                batch = []
                
                # Collect requests for batch processing
                try:
                    # Wait for first request
                    request = await asyncio.wait_for(
                        self.request_queue.get(), 
                        timeout=self.batch_timeout
                    )
                    batch.append(request)
                    
                    # Collect additional requests up to batch size
                    while len(batch) < self.batch_size:
                        try:
                            request = await asyncio.wait_for(
                                self.request_queue.get(), 
                                timeout=0.1
                            )
                            batch.append(request)
                        except asyncio.TimeoutError:
                            break
                            
                except asyncio.TimeoutError:
                    # No requests in timeout period, continue
                    continue
                
                # Process batch if we have requests
                if batch:
                    logger.debug(f"Processing batch of {len(batch)} requests")
                    # In a real implementation, you'd optimize similar requests
                    # For now, process individually
                    tasks = [self._process_single_request(req) for req in batch]
                    await asyncio.gather(*tasks, return_exceptions=True)
                    
            except Exception as e:
                logger.error(f"Error in batch processor: {e}")
                await asyncio.sleep(1)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get optimizer statistics"""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': self.successful_requests / max(self.total_requests, 1),
            'circuit_breaker_state': self.circuit_breaker_state.value,
            'circuit_breaker_failures': self.circuit_breaker_failures,
            'circuit_breaker_trips': self.circuit_breaker_trips,
            'rate_limited_requests': self.rate_limited_requests,
            'current_rate_window_requests': len(self.request_times),
            'queue_size': self.request_queue.qsize() if hasattr(self.request_queue, 'qsize') else 0
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.circuit_breaker_trips = 0
        self.rate_limited_requests = 0
    
    async def shutdown(self):
        """Shutdown the optimizer"""
        self.batch_processor_running = False
        if self._batch_processor_task:
            self._batch_processor_task.cancel()
            try:
                await self._batch_processor_task
            except asyncio.CancelledError:
                pass
        logger.info("AI Request Optimizer shutdown")

# Global AI optimizer instance
ai_optimizer = AIRequestOptimizer()

# Convenience decorators
def ai_optimized(timeout: float = 30.0, retries: int = 1, priority: int = 1):
    """Decorator to optimize AI function calls"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await ai_optimizer.execute_ai_request(func, *args, **kwargs)
        return wrapper
    return decorator

def batch_ai_requests(batch_size: int = 5, timeout: float = 1.0):
    """Decorator to batch similar AI requests"""
    def decorator(func):
        # This would require more complex implementation for automatic batching
        # For now, just use the optimizer
        async def wrapper(*args, **kwargs):
            return await ai_optimizer.execute_ai_request(func, *args, **kwargs)
        return wrapper
    return decorator
