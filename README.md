# Jai MCP Server

MCP (Model Context Protocol) server for managing Jai platform resources through Claude Code.

## Overview

The Jai MCP server enables natural language interactions with the Jai platform, allowing developers to:
- Create and manage modules with examples
- Set up projects from blueprints
- Monitor platform health
- Manage teams and permissions

## Installation

```bash
npm install -g jai-mcp
```

## Usage

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "jai": {
      "command": "jai-mcp",
      "args": ["--api-key", "YOUR_API_KEY"]
    }
  }
}
```

## Features

- **Module Management**: Create, update, and list modules
- **Project Setup**: Initialize projects with blueprints
- **Health Monitoring**: Check platform status and endpoints
- **Team Management**: Create teams and manage permissions

## Development

```bash
npm install
npm run dev
```

## License

MIT