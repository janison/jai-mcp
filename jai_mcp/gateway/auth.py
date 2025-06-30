"""Authentication and authorization for MCP-API Gateway."""

import logging
import os
from typing import Dict, Any, Optional

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger("jai-mcp.gateway.auth")

# Security scheme
security = HTTPBearer()

# Configuration
ALLOWED_ADMINS = os.getenv("JAI_ALLOWED_ADMINS", "").split(",")
ALLOWED_ADMINS = [admin.strip() for admin in ALLOWED_ADMINS if admin.strip()]


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify the API key from the Authorization header."""
    if not credentials:
        raise HTTPException(status_code=401, detail="API key required")
    
    api_key = credentials.credentials
    
    # TODO: Implement actual API key validation
    # This would typically involve:
    # 1. Checking against a database or key management service
    # 2. Validating key format and expiration
    # 3. Rate limiting per key
    
    if not api_key or len(api_key) < 32:  # Basic validation
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key


async def get_user_from_api_key(api_key: str) -> Dict[str, Any]:
    """Get user information from API key."""
    # TODO: Implement actual user lookup
    # This would typically involve:
    # 1. Database lookup of user associated with API key
    # 2. Retrieving user roles and permissions
    # 3. Caching for performance
    
    # For now, return a mock user
    # In production, this would be a database lookup
    return {
        "id": "admin-user-123",
        "email": "admin@example.com",
        "roles": ["system_admin"],
        "tenant_id": "default",
        "permissions": ["mcp_access", "module_management", "project_management"],
    }


async def verify_admin_access(api_key: str = Depends(verify_api_key)) -> Dict[str, Any]:
    """Verify that the user has admin access rights."""
    user = await get_user_from_api_key(api_key)
    
    # Check if user has admin role
    user_roles = user.get("roles", [])
    admin_roles = ["system_admin", "org_admin"]
    
    if not any(role in admin_roles for role in user_roles):
        logger.warning(f"Non-admin user attempted MCP access: {user.get('email')}")
        raise HTTPException(
            status_code=403,
            detail="MCP access requires admin privileges"
        )
    
    # Check if user is in allowed admins list (if configured)
    if ALLOWED_ADMINS:
        user_email = user.get("email", "")
        if user_email not in ALLOWED_ADMINS:
            logger.warning(f"Unauthorized admin attempted access: {user_email}")
            raise HTTPException(
                status_code=403,
                detail="Admin not authorized for MCP access"
            )
    
    logger.info(f"Admin access granted: {user.get('email')}")
    return user


async def get_tenant_from_request(request: Request) -> str:
    """Extract tenant ID from request headers."""
    tenant_id = request.headers.get("X-Tenant-ID")
    
    if not tenant_id:
        raise HTTPException(
            status_code=400,
            detail="Tenant ID required in X-Tenant-ID header"
        )
    
    return tenant_id


async def verify_tenant_access(
    tenant: str = Depends(get_tenant_from_request),
    user: Dict[str, Any] = Depends(verify_admin_access),
) -> str:
    """Verify that the user has access to the specified tenant."""
    user_tenant = user.get("tenant_id")
    
    # System admins can access any tenant
    if "system_admin" in user.get("roles", []):
        return tenant
    
    # Org admins can only access their own tenant
    if user_tenant != tenant:
        logger.warning(
            f"Cross-tenant access attempt: user {user.get('email')} "
            f"tried to access tenant {tenant} (user tenant: {user_tenant})"
        )
        raise HTTPException(
            status_code=403,
            detail="Cross-tenant access denied"
        )
    
    return tenant