# src/utils/circuit_breaker.py
import asyncio
import time
import logging
from typing import Callable, Any
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60, 
                 half_open_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_timeout = half_open_timeout
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.last_attempt_time = None
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        self.last_attempt_time = time.time()
        
        if self.state == CircuitState.OPEN:
            if self._should_try_again():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN state")
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            result = await self._execute_function(func, *args, **kwargs)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise
    
    async def _execute_function(self, func: Callable, *args, **kwargs) -> Any:
        """Execute the function with appropriate async handling"""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            # Run synchronous function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)
    
    def _on_success(self):
        """Handle successful execution"""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker transitioning to CLOSED state")
        
        self.failure_count = 0
        self.last_failure_time = None
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if (self.state == CircuitState.CLOSED and 
            self.failure_count >= self.failure_threshold):
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker transitioning to OPEN state "
                          f"({self.failure_count} failures)")
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker transitioning back to OPEN state "
                          "after failed half-open attempt")
    
    def _should_try_again(self) -> bool:
        """Check if we should attempt to execute in OPEN state"""
        if not self.last_failure_time:
            return True
        
        time_since_failure = time.time() - self.last_failure_time
        
        if self.state == CircuitState.OPEN:
            return time_since_failure >= self.timeout
        elif self.state == CircuitState.HALF_OPEN:
            return time_since_failure >= self.half_open_timeout
        
        return True
    
    def get_state(self) -> CircuitState:
        """Get current circuit breaker state"""
        return self.state
    
    def get_metrics(self) -> dict:
        """Get circuit breaker metrics"""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'last_failure_time': self.last_failure_time,
            'last_attempt_time': self.last_attempt_time
        }
    
    def reset(self):
        """Reset circuit breaker to initial state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.last_attempt_time = None
        logger.info("Circuit breaker reset to CLOSED state")

class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass
