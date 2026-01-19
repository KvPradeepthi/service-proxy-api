"""Configuration module for the proxy service."""

import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    
    # Flask settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # External Service Configuration
    EXTERNAL_SERVICE_URL = os.getenv(
        'EXTERNAL_SERVICE_URL',
        'http://localhost:5001/external-api/process'
    )
    
    # Rate Limiter Configuration
    RATE_LIMIT_WINDOW_SECONDS = int(os.getenv('RATE_LIMIT_WINDOW_SECONDS', 60))
    RATE_LIMIT_MAX_REQUESTS = int(os.getenv('RATE_LIMIT_MAX_REQUESTS', 10))
    
    # Circuit Breaker Configuration
    CB_FAILURE_THRESHOLD = int(os.getenv('CB_FAILURE_THRESHOLD', 5))
    CB_RESET_TIMEOUT_SECONDS = int(os.getenv('CB_RESET_TIMEOUT_SECONDS', 30))
    CB_HALF_OPEN_MAX_CALLS = int(os.getenv('CB_HALF_OPEN_MAX_CALLS', 2))
    
    # Retry Strategy Configuration
    RETRY_MAX_ATTEMPTS = int(os.getenv('RETRY_MAX_ATTEMPTS', 3))
    RETRY_INITIAL_DELAY_MS = int(os.getenv('RETRY_INITIAL_DELAY_MS', 100))
    RETRY_BACKOFF_MULTIPLIER = float(os.getenv('RETRY_BACKOFF_MULTIPLIER', 2.0))
    RETRY_MAX_DELAY_MS = int(os.getenv('RETRY_MAX_DELAY_MS', 5000))
    
    # Request timeout (in seconds)
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 10))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    RATE_LIMIT_WINDOW_SECONDS = 10
    RATE_LIMIT_MAX_REQUESTS = 5
    CB_FAILURE_THRESHOLD = 2
    CB_RESET_TIMEOUT_SECONDS = 5


def get_config():
    """Get appropriate config based on environment."""
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
