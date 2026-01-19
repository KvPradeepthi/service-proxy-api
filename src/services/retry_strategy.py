"""Retry Strategy with Exponential Backoff."""

import time
import logging
import random
from typing import Callable, Any, Type, Tuple

logger = logging.getLogger(__name__)


class RetryStrategy:
    """Exponential backoff retry strategy."""
    
    def __init__(self, max_attempts: int = 3, initial_delay_ms: int = 100,
                 backoff_multiplier: float = 2.0, max_delay_ms: int = 5000,
                 jitter: bool = True):
        """
        Initialize Retry Strategy.
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay_ms: Initial delay in milliseconds
            backoff_multiplier: Exponential backoff multiplier
            max_delay_ms: Maximum delay cap in milliseconds
            jitter: Add random jitter to delays
        """
        self.max_attempts = max_attempts
        self.initial_delay_ms = initial_delay_ms
        self.backoff_multiplier = backoff_multiplier
        self.max_delay_ms = max_delay_ms
        self.jitter = jitter
    
    def execute(self, func: Callable, *args: Any,
                retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
                **kwargs: Any) -> Any:
        """Execute function with retry logic."""
        attempt = 0
        last_exception = None
        
        while attempt < self.max_attempts:
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f'Succeeded on retry attempt {attempt}')
                return result
            except retryable_exceptions as e:
                last_exception = e
                attempt += 1
                
                if attempt < self.max_attempts:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f'Attempt {attempt} failed: {str(e)}. '
                        f'Retrying in {delay}ms...'
                    )
                    time.sleep(delay / 1000.0)
                else:
                    logger.error(
                        f'All {self.max_attempts} attempts failed. '
                        f'Last error: {str(e)}'
                    )
        
        if last_exception:
            raise last_exception
    
    def _calculate_delay(self, attempt: int) -> int:
        """Calculate delay for given attempt with exponential backoff."""
        delay_ms = int(
            self.initial_delay_ms * (self.backoff_multiplier ** (attempt - 1))
        )
        
        # Cap maximum delay
        delay_ms = min(delay_ms, self.max_delay_ms)
        
        # Add jitter if enabled
        if self.jitter:
            jitter_ms = random.randint(0, delay_ms // 2)
            delay_ms += jitter_ms
        
        return delay_ms
    
    def get_retry_info(self, attempt: int) -> dict:
        """Get retry information for given attempt."""
        return {
            'attempt': attempt,
            'max_attempts': self.max_attempts,
            'delay_ms': self._calculate_delay(attempt),
            'can_retry': attempt < self.max_attempts
        }
