# Service Proxy API with Circuit Breaker and Rate Limiting

A resilient external service proxy API with Circuit Breaker pattern, Rate Limiting, and Retry Strategy with exponential backoff for building fault-tolerant backend systems.

## Features

- **Circuit Breaker Pattern**: Intelligent failure handling with CLOSED, OPEN, and HALF-OPEN states
- **Rate Limiting**: Per-client request throttling with configurable windows and limits
- **Retry Strategy**: Exponential backoff retry mechanism for transient failures
- **Health Check Endpoint**: Monitor service availability
- **Docker Support**: Fully containerized with docker-compose orchestration
- **Comprehensive Testing**: Unit and integration tests included

## Project Structure

```
service-proxy-api/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── services/
│   │   ├── circuit_breaker.py
│   │   ├── rate_limiter.py
│   │   ├── retry_strategy.py
│   │   └── external_service_client.py
│   └── api/
│       └── proxy_routes.py
├── external_mock_service/
│   ├── app.py
│   └── Dockerfile
├── tests/
│   ├── unit/
│   └── integration/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- curl (for testing)

### Running with Docker Compose

```bash
# Clone the repository
git clone https://github.com/KvPradeepthi/service-proxy-api.git
cd service-proxy-api

# Start services
docker-compose up --build

# Test the health endpoint
curl http://localhost:8000/health
```

## API Endpoints

### POST /api/proxy/data
Forward requests to external service with resilience patterns.

**Request:**
```json
{
  "message": "Hello from client"
}
```

**Response (Success - 200):**
```json
{
  "status": "success",
  "external_response": {...},
  "proxy_notes": ""
}
```

**Response (Rate Limited - 429):**
```json
{
  "status": "error",
  "message": "Rate limit exceeded. Please try again later."
}
```

**Response (Circuit Open - 503):**
```json
{
  "status": "error",
  "message": "External service is currently unavailable (Circuit Open)."
}
```

### GET /health
Service health check endpoint.

**Response (200):**
```json
{
  "status": "healthy"
}
```

## Environment Variables

### Rate Limiting
- `RATE_LIMIT_WINDOW_SECONDS`: Time window for rate limiting (default: 60)
- `RATE_LIMIT_MAX_REQUESTS`: Max requests per window (default: 10)

### Circuit Breaker
- `CB_FAILURE_THRESHOLD`: Consecutive failures to open circuit (default: 5)
- `CB_RESET_TIMEOUT_SECONDS`: Time before transitioning to HALF-OPEN (default: 30)

### Retry Strategy
- `RETRY_MAX_ATTEMPTS`: Maximum retry attempts (default: 3)
- `RETRY_INITIAL_DELAY_MS`: Initial delay in ms (default: 100)
- `RETRY_BACKOFF_MULTIPLIER`: Exponential backoff multiplier (default: 2.0)

### External Service
- `EXTERNAL_SERVICE_URL`: URL of external service to proxy
- `EXTERNAL_FAIL_RATE`: Mock service failure rate (0.0-1.0)
- `EXTERNAL_LATENCY_MS`: Mock service latency in ms

## Implementation Details

### Circuit Breaker States

1. **CLOSED**: Normal operation, requests pass through
2. **OPEN**: Failures exceeded threshold, requests immediately rejected
3. **HALF-OPEN**: Testing if service recovered, limited requests allowed

### Rate Limiting Algorithm
Implements Sliding Window Counter for accurate per-client limiting.

### Retry Strategy
Exponential backoff with jitter:
```
delay = initial_delay * (multiplier ^ attempt)
```

## Testing

### Run Unit Tests
```bash
docker-compose exec proxy-service python -m pytest tests/unit/ -v
```

### Run Integration Tests
```bash
docker-compose exec proxy-service python -m pytest tests/integration/ -v
```

### Run All Tests
```bash
docker-compose exec proxy-service python -m pytest tests/ -v
```

## Example Usage

```bash
# Test successful request
curl -X POST http://localhost:8000/api/proxy/data \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# Test rate limiting (send 11 requests within 60 seconds)
for i in {1..11}; do
  curl -X POST http://localhost:8000/api/proxy/data \
    -H "Content-Type: application/json" \
    -d '{"request_number": '$i'}'
done
```

## Troubleshooting

### Services won't start
- Check Docker is running: `docker ps`
- Check ports 8000 and 5001 are available
- View logs: `docker-compose logs -f`

### Health check failing
- Verify proxy service is running: `docker-compose ps`
- Check logs: `docker-compose logs proxy-service`

## Technologies Used

- **Framework**: Flask
- **Language**: Python 3.11
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest

## Future Enhancements

- Redis integration for distributed state management
- Metrics collection with Prometheus
- Distributed tracing with Jaeger
- Advanced rate limiting algorithms
- Load balancing strategies

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT
