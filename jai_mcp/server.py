#!/usr/bin/env python
"""Jai MCP Server - FastMCP-based server for Jai platform management."""

import logging
import os
import sys
from pathlib import Path

from fastmcp import FastMCP

# Create FastMCP instance
mcp = FastMCP("jai-mcp")

# Import configuration
from .config import (
    JAI_API_KEY,
    JAI_TENANT,
    JAI_MCP_ENDPOINT,
    DEBUG,
    setup_logging,
)

# Auto-import all tools
from . import tools


def main():
    """Run the Jai MCP server."""
    # Set up logging
    logger = setup_logging()
    
    # Check for required configuration
    missing_config = []
    if not JAI_API_KEY:
        missing_config.append("JAI_API_KEY")
    if not JAI_TENANT:
        missing_config.append("JAI_TENANT")
    if not JAI_MCP_ENDPOINT:
        missing_config.append("JAI_MCP_ENDPOINT")
    
    if missing_config:
        logger.error(f"Missing required configuration: {', '.join(missing_config)}")
        logger.error("Please set the required environment variables or create a .env file")
        logger.error("Example:")
        for var in missing_config:
            logger.error(f"  export {var}=your-value")
        sys.exit(1)
    
    # Log startup information
    logger.info("Starting Jai MCP Server")
    logger.info(f"Tenant: {JAI_TENANT}")
    logger.info(f"MCP Endpoint: {JAI_MCP_ENDPOINT}")
    logger.info(f"Debug mode: {DEBUG}")
    
    # Run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()