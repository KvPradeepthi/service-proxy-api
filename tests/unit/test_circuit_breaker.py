"""Unit tests for Circuit Breaker."""

import pytest
import time
from src.services.circuit_breaker import CircuitBreaker, CircuitState


def test_circuit_breaker_initial_state():
    """Test circuit breaker starts in CLOSED state."""
    cb = CircuitBreaker()
    assert cb.get_state() == 'CLOSED'


def test_circuit_breaker_opens_after_failures():
    """Test circuit breaker opens after threshold failures."""
    cb = CircuitBreaker(failure_threshold=2)
    
    def failing_func():
        raise Exception('Test failure')
    
    # First failure
    with pytest.raises(Exception):
        cb.call(failing_func)
    assert cb.get_state() == 'CLOSED'
    
    # Second failure - should open circuit
    with pytest.raises(Exception):
        cb.call(failing_func)
    assert cb.get_state() == 'OPEN'


def test_circuit_breaker_rejects_when_open():
    """Test circuit breaker rejects calls when OPEN."""
    cb = CircuitBreaker(failure_threshold=1)
    
    def failing_func():
        raise Exception('Test failure')
    
    # Open the circuit
    with pytest.raises(Exception):
        cb.call(failing_func)
    
    # Should reject subsequent calls
    with pytest.raises(Exception) as exc_info:
        cb.call(failing_func)
    assert 'Circuit breaker is OPEN' in str(exc_info.value)


def test_circuit_breaker_half_open_success():
    """Test circuit breaker transitions to CLOSED after success in HALF_OPEN."""
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=1, success_threshold=1)
    
    def failing_func():
        raise Exception('Test failure')
    
    def succeeding_func():
        return 'success'
    
    # Open the circuit
    with pytest.raises(Exception):
        cb.call(failing_func)
    assert cb.get_state() == 'OPEN'
    
    # Wait for reset timeout
    time.sleep(1.1)
    
    # Next call should transition to HALF_OPEN and succeed
    result = cb.call(succeeding_func)
    assert result == 'success'
    assert cb.get_state() == 'CLOSED'
