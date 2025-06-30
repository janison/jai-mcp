"""MCP-API Gateway - Secure proxy for Jai platform access."""

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .auth import verify_admin_access, get_tenant_from_request
from .proxy import JaiAPIProxy
from .logging import setup_audit_logging

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Global proxy instance
proxy: JaiAPIProxy = None
audit_logger = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    global proxy, audit_logger
    
    # Startup
    logging.info("Starting MCP-API Gateway")
    proxy = JaiAPIProxy()
    audit_logger = setup_audit_logging()
    
    yield
    
    # Shutdown
    logging.info("Shutting down MCP-API Gateway")
    if proxy:
        await proxy.close()


# Create FastAPI app
app = FastAPI(
    title="Jai MCP-API Gateway",
    description="Secure proxy for Jai platform MCP access",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    """Audit all requests."""
    # Log the request
    if audit_logger:
        audit_logger.info({
            "event": "request_received",
            "method": request.method,
            "path": request.url.path,
            "client_ip": get_remote_address(request),
            "user_agent": request.headers.get("user-agent"),
        })
    
    response = await call_next(request)
    
    # Log the response
    if audit_logger:
        audit_logger.info({
            "event": "request_completed",
            "status_code": response.status_code,
            "path": request.url.path,
        })
    
    return response


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "jai-mcp-gateway"}


# Proxy endpoints
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("60/minute")
async def proxy_request(
    request: Request,
    path: str,
    admin_user: Dict[str, Any] = Depends(verify_admin_access),
    tenant: str = Depends(get_tenant_from_request),
):
    """Proxy requests to the internal Jai API."""
    if not proxy:
        raise HTTPException(status_code=503, detail="Gateway not ready")
    
    try:
        # Forward the request to the internal API
        response_data = await proxy.forward_request(
            method=request.method,
            path=path,
            headers=dict(request.headers),
            body=await request.body() if request.method in ["POST", "PUT"] else None,
            tenant=tenant,
            user=admin_user,
        )
        
        return response_data
        
    except Exception as e:
        logging.error(f"Proxy request failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def main():
    """Run the MCP-API Gateway."""
    # Configuration from environment
    host = os.getenv("GATEWAY_HOST", "0.0.0.0")
    port = int(os.getenv("GATEWAY_PORT", "8080"))
    debug = os.getenv("GATEWAY_DEBUG", "false").lower() == "true"
    
    # Set up logging
    log_level = "debug" if debug else "info"
    logging.basicConfig(level=getattr(logging, log_level.upper()))
    
    # Run the server
    uvicorn.run(
        "jai_mcp.gateway.main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=debug,
    )


if __name__ == "__main__":
    main()