"""Mock external service for testing the proxy."""

from flask import Flask, request, jsonify
import os
import time
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
FAIL_RATE = float(os.getenv('EXTERNAL_FAIL_RATE', '0.2'))
LATENCY_MS = int(os.getenv('EXTERNAL_LATENCY_MS', '50'))


@app.route('/external-api/process', methods=['POST'])
def process_data():
    """Mock external API endpoint."""
    # Apply latency
    time.sleep(LATENCY_MS / 1000.0)
    
    # Simulate failures
    if random.random() < FAIL_RATE:
        logger.warning('Simulating external service failure')
        return jsonify({
            'status': 'error',
            'message': 'Simulated external service failure'
        }), 500
    
    # Process request
    data = request.get_json()
    logger.info(f'Processing request: {data}')
    
    return jsonify({
        'status': 'success',
        'received_data': data,
        'processed_at': time.time(),
        'message': 'Data processed successfully by external service'
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'mock-external-service'
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    logger.info(f'Starting mock external service on port {port}')
    logger.info(f'Configured failure rate: {FAIL_RATE}, latency: {LATENCY_MS}ms')
    app.run(host='0.0.0.0', port=port, debug=False)
