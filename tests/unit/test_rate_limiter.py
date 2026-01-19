import pytest
import time
from datetime import datetime
from src.services.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test suite for Rate Limiter"""

    def test_rate_limiter_initialization(self):
        """Test RateLimiter initializes correctly"""
        limiter = RateLimiter(requests_per_window=10, window_size_seconds=60)
        assert limiter.requests_per_window == 10
        assert limiter.window_size_seconds == 60

    def test_allow_request_within_limit(self):
        """Test requests are allowed within limit"""
        limiter = RateLimiter(requests_per_window=5, window_size_seconds=60)
        
        for _ in range(5):
            assert limiter.is_allowed() == True

    def test_deny_request_exceeding_limit(self):
        """Test requests are denied when limit exceeded"""
        limiter = RateLimiter(requests_per_window=3, window_size_seconds=60)
        
        for _ in range(3):
            assert limiter.is_allowed() == True
        
        assert limiter.is_allowed() == False

    def test_window_reset(self):
        """Test rate limit window resets"""
        limiter = RateLimiter(requests_per_window=2, window_size_seconds=1)
        
        assert limiter.is_allowed() == True
        assert limiter.is_allowed() == True
        assert limiter.is_allowed() == False
        
        time.sleep(1.1)
        
        assert limiter.is_allowed() == True

    def test_concurrent_requests(self):
        """Test rate limiter with multiple threads"""
        import threading
        
        limiter = RateLimiter(requests_per_window=10, window_size_seconds=60)
        allowed_count = [0]
        denied_count = [0]
        
        def make_request():
            if limiter.is_allowed():
                allowed_count[0] += 1
            else:
                denied_count[0] += 1
        
        threads = [threading.Thread(target=make_request) for _ in range(15)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        assert allowed_count[0] == 10
        assert denied_count[0] == 5

    def test_old_timestamps_evicted(self):
        """Test that old request timestamps are evicted"""
        limiter = RateLimiter(requests_per_window=5, window_size_seconds=2)
        
        for _ in range(5):
            assert limiter.is_allowed() == True
        
        time.sleep(2.1)
        
        assert len(limiter.request_times) == 0
        assert limiter.is_allowed() == True
