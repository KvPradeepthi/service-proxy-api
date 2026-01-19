# Service Proxy API Architecture

## System Overview

The Service Proxy API implements a resilient proxy pattern that safeguards external service integrations through three key resilience mechanisms:

1. **Circuit Breaker Pattern** - Prevents cascading failures
2. **Rate Limiting** - Controls resource consumption
3. **Retry Strategy** - Recovers from transient failures

## Component Details

### 1. Circuit Breaker

**States**:
- CLOSED: Normal operation
- OPEN: Failures exceeded, requests fail immediately  
- HALF-OPEN: Testing recovery

**Thresholds**:
- Failure threshold: 5 failures to open
- Success threshold: 2 successes to close
- Timeout: 60 seconds before retry

### 2. Rate Limiter

**Algorithm**: Sliding Window Counter
- Max 10 requests per 60-second window
- Thread-safe tracking of request timestamps
- Automatic eviction of old timestamps

### 3. Retry Strategy

**Algorithm**: Exponential Backoff with Jitter
- Max 3 retries
- Base delay: 1 second
- Max delay: 32 seconds
- Formula: min(1 * 2^attempt + jitter, 32)

## Docker Architecture

**Services**:
- proxy-api: Main Flask app (port 5000)
- external-mock: Mock service (port 5001)
- Bridge network for service communication

## Request Flow

1. Client sends request to /api/proxy/data
2. Rate limiter checks quota
3. Circuit breaker checks state
4. If allowed, ExternalServiceClient makes HTTP call
5. Retry strategy handles transient failures
6. Response returned to client

## Testing

- Unit tests for each resilience pattern
- Integration tests for end-to-end flows
- Mock service with configurable failure rates
- Test coverage for all state transitions
