"""Rate Limiter implementation using Sliding Window Counter."""

import time
import logging
from collections import defaultdict
from typing import Dict, List

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter using Sliding Window Counter algorithm."""
    
    def __init__(self, window_size: int = 60, max_requests: int = 10):
        """
        Initialize the Rate Limiter.
        
        Args:
            window_size: Time window in seconds
            max_requests: Maximum requests allowed per window
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if a request from client is allowed."""
        now = time.time()
        window_start = now - self.window_size
        
        # Remove old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        # Check if request is allowed
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        
        return False
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for a client in current window."""
        now = time.time()
        window_start = now - self.window_size
        
        active_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        return max(0, self.max_requests - len(active_requests))
    
    def get_reset_time(self, client_id: str) -> int:
        """Get time in seconds until limit resets."""
        if not self.requests[client_id]:
            return 0
        
        oldest_request = min(self.requests[client_id])
        reset_time = int(oldest_request + self.window_size - time.time())
        
        return max(0, reset_time)
    
    def cleanup_old_entries(self, max_age: int = 3600) -> None:
        """Clean up entries older than max_age seconds."""
        now = time.time()
        cutoff_time = now - max_age
        
        clients_to_remove = []
        for client_id, requests in self.requests.items():
            if not any(req_time > cutoff_time for req_time in requests):
                clients_to_remove.append(client_id)
        
        for client_id in clients_to_remove:
            del self.requests[client_id]
        
        if clients_to_remove:
            logger.info(f'Cleaned up {len(clients_to_remove)} old rate limit entries')
