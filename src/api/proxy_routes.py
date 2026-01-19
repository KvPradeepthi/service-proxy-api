"""API routes for the proxy service."""

from flask import Blueprint, request, jsonify, current_app
import logging
from src.services.external_service_client import ExternalServiceClient

logger = logging.getLogger(__name__)
proxy_bp = Blueprint('proxy', __name__, url_prefix='/api')


@proxy_bp.route('/proxy/data', methods=['POST'])
def proxy_data():
    """Proxy POST request to external service with resilience patterns."""
    try:
        # Extract client ID from request (IP address)
        client_id = request.remote_addr
        
        # Check rate limit
        if not current_app.rate_limiter.is_allowed(client_id):
            remaining = current_app.rate_limiter.get_remaining_requests(client_id)
            reset_time = current_app.rate_limiter.get_reset_time(client_id)
            return jsonify({
                'status': 'error',
                'message': 'Rate limit exceeded. Please try again later.'
            }), 429
        
        # Get request data
        data = request.get_json()
        
        # Circuit breaker check
        cb_state = current_app.circuit_breaker.get_state()
        if cb_state == 'OPEN':
            logger.warning('Circuit breaker is OPEN, rejecting request')
            return jsonify({
                'status': 'error',
                'message': 'External service is currently unavailable (Circuit Open).'
            }), 503
        
        # Execute with retry strategy
        external_url = current_app.config.get('EXTERNAL_SERVICE_URL')
        client = ExternalServiceClient(external_url)
        
        try:
            external_response = current_app.retry_strategy.execute(
                client.post,
                data=data
            )
            
            # Update circuit breaker on success
            current_app.circuit_breaker._on_success()
            
            return jsonify({
                'status': 'success',
                'external_response': external_response,
                'proxy_notes': f'Circuit breaker state: {cb_state}'
            }), 200
        
        except Exception as e:
            # Update circuit breaker on failure
            current_app.circuit_breaker._on_failure()
            
            logger.error(f'Failed to call external service: {str(e)}')
            return jsonify({
                'status': 'error',
                'message': 'An unexpected error occurred.',
                'circuit_state': current_app.circuit_breaker.get_state()
            }), 500
    
    except Exception as e:
        logger.error(f'Error in proxy_data: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500


@proxy_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'circuit_breaker_state': current_app.circuit_breaker.get_state()
    }), 200
