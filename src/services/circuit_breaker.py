"""Circuit Breaker pattern implementation."""

import time
import logging
from enum import Enum
from typing import Callable, Any

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """Circuit Breaker implementation to handle failures in external services."""
    
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 30,
                 success_threshold: int = 2):
        """
        Initialize the Circuit Breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            reset_timeout: Seconds before transitioning from OPEN to HALF_OPEN
            success_threshold: Number of successes in HALF_OPEN before closing
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_open_time = None
    
    def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info('Circuit breaker transitioning to HALF_OPEN')
            else:
                raise Exception('Circuit breaker is OPEN')
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt reset from OPEN state."""
        if self.last_open_time is None:
            return False
        elapsed = time.time() - self.last_open_time
        return elapsed >= self.reset_timeout
    
    def _on_success(self) -> None:
        """Handle successful call."""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                logger.info('Circuit breaker transitioning to CLOSED')
    
    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.last_open_time = time.time()
            logger.warning('Circuit breaker transitioning to OPEN from HALF_OPEN')
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_open_time = time.time()
            logger.warning(f'Circuit breaker OPEN after {self.failure_count} failures')
    
    def get_state(self) -> str:
        """Get current circuit state."""
        return self.state.value
    
    def reset(self) -> None:
        """Manually reset circuit breaker."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info('Circuit breaker manually reset to CLOSED')
