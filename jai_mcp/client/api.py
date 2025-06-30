"""Jai API client for MCP server."""

import logging
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from ..config import JAI_API_KEY, JAI_MCP_ENDPOINT, JAI_TENANT, REQUEST_TIMEOUT

logger = logging.getLogger("jai-mcp.client")


class JaiAPIError(Exception):
    """Base exception for Jai API errors."""
    pass


class JaiAPIClient:
    """Client for interacting with Jai API through MCP Gateway."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        tenant: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.api_key = api_key or JAI_API_KEY
        self.tenant = tenant or JAI_TENANT
        self.endpoint = endpoint or JAI_MCP_ENDPOINT
        self.timeout = timeout or REQUEST_TIMEOUT
        
        if not all([self.api_key, self.tenant, self.endpoint]):
            raise ValueError("API key, tenant, and endpoint are required")
        
        self.headers = {
            "X-API-Key": self.api_key,
            "X-Tenant-ID": self.tenant,
            "Content-Type": "application/json",
        }
        
        self._client = httpx.AsyncClient(
            base_url=self.endpoint,
            headers=self.headers,
            timeout=self.timeout,
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()
    
    async def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request to the Jai API."""
        try:
            response = await self._client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise JaiAPIError(f"API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise JaiAPIError(f"Request failed: {str(e)}")
    
    async def get(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make a GET request."""
        return await self.request("GET", path, **kwargs)
    
    async def post(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make a POST request."""
        return await self.request("POST", path, **kwargs)
    
    async def put(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self.request("PUT", path, **kwargs)
    
    async def delete(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self.request("DELETE", path, **kwargs)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the Jai platform."""
        return await self.get("/health")


# Singleton instance
_client: Optional[JaiAPIClient] = None


async def get_client() -> JaiAPIClient:
    """Get or create the API client instance."""
    global _client
    if _client is None:
        _client = JaiAPIClient()
    return _client