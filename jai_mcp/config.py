"""Configuration management for Jai MCP server."""

import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# API Configuration
JAI_API_KEY: Optional[str] = os.getenv("JAI_API_KEY")
JAI_TENANT: Optional[str] = os.getenv("JAI_TENANT")
JAI_MCP_ENDPOINT: Optional[str] = os.getenv("JAI_MCP_ENDPOINT", "https://mcp.jai.com")

# Debug Configuration
DEBUG: bool = os.getenv("JAI_DEBUG", "false").lower() == "true"
LOG_LEVEL: str = os.getenv("JAI_LOG_LEVEL", "INFO")

# Rate Limiting
RATE_LIMIT_REQUESTS: int = int(os.getenv("JAI_RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW: int = int(os.getenv("JAI_RATE_LIMIT_WINDOW", "60"))  # seconds

# Timeout Configuration
REQUEST_TIMEOUT: int = int(os.getenv("JAI_REQUEST_TIMEOUT", "30"))  # seconds

# Cache Configuration
CACHE_TTL: int = int(os.getenv("JAI_CACHE_TTL", "300"))  # seconds


def setup_logging() -> logging.Logger:
    """Set up logging configuration."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Get logger for our application
    logger = logging.getLogger("jai-mcp")
    
    # Adjust log level for HTTP requests if not in debug mode
    if not DEBUG:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    return logger