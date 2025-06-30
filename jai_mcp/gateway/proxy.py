"""API proxy for forwarding requests to internal Jai API."""

import logging
import os
from typing import Dict, Any, Optional, Union

import httpx

logger = logging.getLogger("jai-mcp.gateway.proxy")


class JaiAPIProxy:
    """Proxy for forwarding MCP requests to internal Jai API."""
    
    def __init__(self):
        self.internal_api_url = os.getenv("JAI_INTERNAL_API_URL", "http://localhost:8000")
        self.timeout = int(os.getenv("JAI_PROXY_TIMEOUT", "30"))
        
        # Create HTTP client for internal API
        self._client = httpx.AsyncClient(
            base_url=self.internal_api_url,
            timeout=self.timeout,
        )
        
        logger.info(f"Proxy initialized for internal API: {self.internal_api_url}")
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def forward_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[bytes] = None,
        tenant: str = None,
        user: Dict[str, Any] = None,
    ) -> Union[Dict[str, Any], bytes]:
        """Forward a request to the internal Jai API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path to forward to
            headers: Request headers
            body: Request body (for POST/PUT)
            tenant: Tenant ID
            user: User information from auth
            
        Returns:
            Response data from internal API
        """
        try:
            # Prepare headers for internal API
            internal_headers = self._prepare_internal_headers(headers, tenant, user)
            
            # Remove hop-by-hop headers
            hop_by_hop_headers = {
                "connection", "keep-alive", "proxy-authenticate",
                "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"
            }
            for header in hop_by_hop_headers:
                internal_headers.pop(header, None)
            
            # Make request to internal API
            response = await self._client.request(
                method=method,
                url=f"/{path.lstrip('/')}",
                headers=internal_headers,
                content=body,
            )
            
            # Log the request
            logger.info(
                f"Proxied {method} /{path} -> {response.status_code} "
                f"(user: {user.get('email', 'unknown')}, tenant: {tenant})"
            )
            
            # Handle response
            if response.status_code >= 400:
                logger.warning(f"Internal API error {response.status_code}: {response.text}")
                response.raise_for_status()
            
            # Return JSON if possible, otherwise raw bytes
            try:
                return response.json()
            except ValueError:
                return response.content
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from internal API: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error to internal API: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in proxy: {str(e)}")
            raise
    
    def _prepare_internal_headers(
        self,
        original_headers: Dict[str, str],
        tenant: str,
        user: Dict[str, Any],
    ) -> Dict[str, str]:
        """Prepare headers for the internal API request."""
        headers = original_headers.copy()
        
        # Add/override headers for internal API
        headers.update({
            "X-Forwarded-For": headers.get("x-forwarded-for", "unknown"),
            "X-Forwarded-Proto": "https",
            "X-Gateway-User-ID": user.get("id", "unknown"),
            "X-Gateway-User-Email": user.get("email", "unknown"),
            "X-Gateway-User-Roles": ",".join(user.get("roles", [])),
            "X-Gateway-Tenant-ID": tenant,
            "X-Gateway-Source": "mcp-gateway",
        })
        
        # Remove authorization header (gateway handles auth)
        headers.pop("authorization", None)
        
        # Add internal API key if configured
        internal_api_key = os.getenv("JAI_INTERNAL_API_KEY")
        if internal_api_key:
            headers["X-Internal-API-Key"] = internal_api_key
        
        return headers