#!/usr/bin/env python3
"""Main entry point for the resilient proxy API service."""

import os
import logging
from flask import Flask
from config import Config
from api.proxy_routes import proxy_bp
from services.circuit_breaker import CircuitBreaker
from services.rate_limiter import RateLimiter
from services.retry_strategy import RetryStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize resilience patterns
    app.circuit_breaker = CircuitBreaker(
        failure_threshold=int(os.getenv('CB_FAILURE_THRESHOLD', 5)),
        reset_timeout=int(os.getenv('CB_RESET_TIMEOUT_SECONDS', 30))
    )
    
    app.rate_limiter = RateLimiter(
        window_size=int(os.getenv('RATE_LIMIT_WINDOW_SECONDS', 60)),
        max_requests=int(os.getenv('RATE_LIMIT_MAX_REQUESTS', 10))
    )
    
    app.retry_strategy = RetryStrategy(
        max_attempts=int(os.getenv('RETRY_MAX_ATTEMPTS', 3)),
        initial_delay_ms=int(os.getenv('RETRY_INITIAL_DELAY_MS', 100)),
        backoff_multiplier=float(os.getenv('RETRY_BACKOFF_MULTIPLIER', 2.0))
    )
    
    # Register blueprints
    app.register_blueprint(proxy_bp)
    
    logger.info('Proxy service initialized successfully')
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('DEBUG', False))
