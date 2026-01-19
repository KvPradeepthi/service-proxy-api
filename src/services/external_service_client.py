"""External service HTTP client."""

import requests
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ExternalServiceClient:
    """Client for calling external services."""
    
    def __init__(self, base_url: str, timeout: int = 10):
        """
        Initialize External Service Client.
        
        Args:
            base_url: Base URL of external service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
    
    def post(self, endpoint: str = '', data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make POST request to external service."""
        url = f"{self.base_url}/{endpoint}".rstrip('/')
        
        try:
            logger.debug(f'Calling external service: {url}')
            response = self.session.post(
                url,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f'Request to {url} timed out')
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f'Connection error to {url}')
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f'HTTP error from {url}: {e.response.status_code}')
            raise
        except Exception as e:
            logger.error(f'Unexpected error calling {url}: {str(e)}')
            raise
    
    def get(self, endpoint: str = '') -> Dict[str, Any]:
        """Make GET request to external service."""
        url = f"{self.base_url}/{endpoint}".rstrip('/')
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f'Error calling {url}: {str(e)}')
            raise
    
    def close(self) -> None:
        """Close session."""
        self.session.close()
