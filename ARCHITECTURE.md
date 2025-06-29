# Jai MCP Server Architecture

## Overview

The Jai MCP server needs to support multi-tenant environments while maintaining security and network isolation. This document outlines the architecture to achieve these goals.

## Key Challenges

1. **Multi-tenancy**: Multiple client implementations with private environments
2. **Security**: Only system/org admins should have MCP access
3. **Network Isolation**: Core API is GCP-internal only

## Proposed Architecture

```
┌─────────────────┐         ┌─────────────────────┐         ┌──────────────────┐
│  Claude Code    │  HTTPS  │  MCP-API Gateway    │  VPC    │  Jai Core API   │
│  (User's Local) │◄────────┤  (Public Endpoint)  │◄────────┤  (GCP Internal)  │
└─────────────────┘         └─────────────────────┘         └──────────────────┘
        │                            │                               ▲
        │                            │                               │
        ▼                            ▼                               │
┌─────────────────┐         ┌─────────────────────┐                │
│  jai-mcp        │         │  Auth Service       │                │
│  (Local MCP)    │         │  - Admin validation │────────────────┘
└─────────────────┘         │  - Tenant routing   │
                            └─────────────────────┘
```

## Components

### 1. Local MCP Server (jai-mcp)
- Runs on developer's machine via Claude Code
- Connects to tenant-specific MCP-API Gateway
- Handles tool definitions and request formatting

### 2. MCP-API Gateway (New Component)
- **Optional** deployment per environment
- Public HTTPS endpoint with strict authentication
- Acts as proxy to internal Jai API
- Features:
  - Rate limiting
  - Request validation
  - Audit logging
  - Admin-only authentication
  - Tenant isolation

### 3. Authentication Flow

```typescript
// Configuration in Claude Code
{
  "mcpServers": {
    "jai": {
      "command": "jai-mcp",
      "env": {
        "JAI_TENANT": "client-name",
        "JAI_MCP_ENDPOINT": "https://mcp.client-name.jai.com",
        "JAI_API_KEY": "admin-api-key"
      }
    }
  }
}
```

## Implementation Approach

### Phase 1: MCP-API Gateway
```
mcp-api-gateway/
├── auth/
│   ├── admin_validator.py     # Verify admin permissions
│   └── tenant_resolver.py     # Route to correct environment
├── proxy/
│   ├── api_proxy.py          # Forward to internal API
│   └── rate_limiter.py       # Prevent abuse
├── logging/
│   └── audit_logger.py       # Track all MCP operations
└── main.py                   # FastAPI application
```

### Phase 2: Deployment Options

1. **Standard Deployment** (for clients wanting MCP):
   ```yaml
   # Cloud Run service
   - name: jai-mcp-gateway
     image: gcr.io/jai-platform/mcp-gateway
     env:
       - INTERNAL_API_URL: http://jai-api.internal
       - ALLOWED_ADMINS: "admin@client.com"
   ```

2. **No Deployment** (default):
   - Clients without MCP needs simply don't deploy the gateway
   - No security exposure for the core API

### Phase 3: Security Model

```python
# Example permission check
async def validate_mcp_access(request: Request):
    # 1. Validate API key
    api_key = request.headers.get("X-API-Key")
    if not validate_api_key(api_key):
        raise HTTPException(401)
    
    # 2. Check admin role
    user = await get_user_from_key(api_key)
    if not user.has_role(["system_admin", "org_admin"]):
        raise HTTPException(403, "MCP access requires admin privileges")
    
    # 3. Verify tenant match
    if user.tenant_id != request.tenant_id:
        raise HTTPException(403, "Cross-tenant access denied")
```

## Benefits

1. **Opt-in**: Only environments that need MCP deploy the gateway
2. **Secure**: Core API remains GCP-internal
3. **Auditable**: All MCP operations are logged
4. **Scalable**: Each tenant has isolated gateway
5. **Flexible**: Easy to add/remove MCP access per environment

## Configuration Example

```yaml
# jai-platform/environments/client-abc/mcp-config.yaml
enabled: true
allowed_admins:
  - admin@client-abc.com
  - sysadmin@client-abc.com
rate_limits:
  requests_per_minute: 60
  burst: 100
allowed_operations:
  - module_management
  - project_creation
  - health_monitoring
  # - deployment (disabled for this client)
```

## Next Steps

1. Validate this architecture with the team
2. Create MCP-API Gateway repository
3. Define exact API endpoints needed
4. Implement authentication service integration
5. Create deployment templates