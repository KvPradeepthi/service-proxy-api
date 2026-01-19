import pytest
import time
from unittest.mock import Mock, patch
from src.services.retry_strategy import RetryStrategy


class TestRetryStrategy:
    """Test suite for Retry Strategy"""

    def test_retry_strategy_initialization(self):
        """Test RetryStrategy initializes correctly"""
        strategy = RetryStrategy(max_retries=3, base_delay=1.0, max_delay=32.0)
        assert strategy.max_retries == 3
        assert strategy.base_delay == 1.0
        assert strategy.max_delay == 32.0

    def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation"""
        strategy = RetryStrategy(max_retries=3, base_delay=1.0, max_delay=32.0)
        
        delay_0 = strategy.calculate_backoff_delay(0)
        delay_1 = strategy.calculate_backoff_delay(1)
        delay_2 = strategy.calculate_backoff_delay(2)
        
        # Delays should increase exponentially
        assert delay_0 < delay_1 < delay_2
        # Should not exceed max_delay
        assert delay_2 <= 32.0

    def test_max_delay_cap(self):
        """Test that delays are capped at max_delay"""
        strategy = RetryStrategy(max_retries=10, base_delay=2.0, max_delay=10.0)
        
        delay = strategy.calculate_backoff_delay(10)
        assert delay <= 10.0

    def test_successful_retry(self):
        """Test successful operation on retry"""
        call_count = [0]
        
        def failing_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception("Transient error")
            return "Success"
        
        strategy = RetryStrategy(max_retries=3, base_delay=0.1)
        result = strategy.execute_with_retry(failing_function)
        
        assert result == "Success"
        assert call_count[0] == 3

    def test_all_retries_exhausted(self):
        """Test when all retries are exhausted"""
        def always_fails():
            raise Exception("Persistent error")
        
        strategy = RetryStrategy(max_retries=2, base_delay=0.1)
        
        with pytest.raises(Exception) as exc_info:
            strategy.execute_with_retry(always_fails)
        
        assert "Persistent error" in str(exc_info.value)

    def test_retry_with_wait_time(self):
        """Test that retry strategy actually waits"""
        call_count = [0]
        call_times = []
        
        def failing_then_success():
            call_count[0] += 1
            call_times.append(time.time())
            if call_count[0] < 2:
                raise Exception("Error")
            return "Success"
        
        strategy = RetryStrategy(max_retries=2, base_delay=0.2, jitter=False)
        start_time = time.time()
        result = strategy.execute_with_retry(failing_then_success)
        end_time = time.time()
        
        assert result == "Success"
        # Should have waited at least base_delay
        assert (end_time - start_time) >= 0.2

    def test_retryable_exceptions(self):
        """Test that only retryable exceptions are retried"""
        strategy = RetryStrategy(max_retries=3, base_delay=0.1)
        
        # ConnectionError should be retried
        call_count = [0]
        
        def connection_error_func():
            call_count[0] += 1
            if call_count[0] == 1:
                raise ConnectionError("Connection failed")
            return "Success"
        
        result = strategy.execute_with_retry(connection_error_func)
        assert result == "Success"
        assert call_count[0] == 2
