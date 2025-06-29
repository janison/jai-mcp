# Jai MCP Project Structure

This repository contains both the local MCP server and the optional MCP-API Gateway.

```
jai-mcp/
├── packages/
│   ├── mcp-server/          # Local MCP server (runs on developer machine)
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── tools/
│   │   │   └── client/
│   │   └── package.json
│   │
│   └── mcp-gateway/         # Optional gateway (deploys to GCP)
│       ├── src/
│       │   ├── main.py
│       │   ├── auth/
│       │   ├── proxy/
│       │   └── logging/
│       ├── Dockerfile
│       └── requirements.txt
│
├── shared/                  # Shared types and utilities
│   ├── types.ts
│   └── constants.ts
│
├── deployment/              # Deployment configurations
│   ├── gateway/
│   │   ├── cloudbuild.yaml
│   │   └── service.yaml
│   └── examples/
│       └── client-config.yaml
│
├── docs/
│   ├── setup-guide.md
│   └── admin-guide.md
│
├── package.json             # Root workspace
└── README.md
```

## Benefits of Monorepo Approach

1. **Shared Types**: Gateway and MCP server share API contracts
2. **Unified Testing**: End-to-end tests across both components
3. **Simpler Deployment**: Single CI/CD pipeline
4. **Version Sync**: Both components always compatible
5. **Easier Development**: One repository to clone and develop

## Development Workflow

```bash
# Install all dependencies
npm install

# Develop MCP server
npm run dev:server

# Develop gateway
npm run dev:gateway

# Build everything
npm run build

# Deploy gateway to client environment
npm run deploy:gateway -- --env=client-abc
```