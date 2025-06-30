"""Audit logging for MCP-API Gateway."""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configure structured logging
class AuditLogFormatter(logging.Formatter):
    """Custom formatter for audit logs."""
    
    def format(self, record):
        # Create base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
        }
        
        # Add message data if it's a dict
        if isinstance(record.msg, dict):
            log_entry.update(record.msg)
        else:
            log_entry["message"] = str(record.msg)
        
        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in {"name", "msg", "args", "levelname", "levelno", "pathname", 
                          "filename", "module", "exc_info", "exc_text", "stack_info",
                          "lineno", "funcName", "created", "msecs", "relativeCreated",
                          "thread", "threadName", "processName", "process", "message"}:
                log_entry[key] = value
        
        return json.dumps(log_entry)


def setup_audit_logging() -> Optional[logging.Logger]:
    """Set up audit logging for the gateway."""
    audit_enabled = os.getenv("JAI_AUDIT_ENABLED", "true").lower() == "true"
    
    if not audit_enabled:
        return None
    
    # Create audit logger
    audit_logger = logging.getLogger("jai-mcp.gateway.audit")
    audit_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in audit_logger.handlers[:]:
        audit_logger.removeHandler(handler)
    
    # Configure audit log destination
    audit_log_file = os.getenv("JAI_AUDIT_LOG_FILE")
    
    if audit_log_file:
        # File handler
        handler = logging.FileHandler(audit_log_file)
    else:
        # Console handler (for Cloud Logging)
        handler = logging.StreamHandler()
    
    # Set formatter
    handler.setFormatter(AuditLogFormatter())
    audit_logger.addHandler(handler)
    
    # Don't propagate to root logger
    audit_logger.propagate = False
    
    return audit_logger


def log_mcp_operation(
    audit_logger: logging.Logger,
    operation: str,
    user: Dict[str, Any],
    tenant: str,
    details: Optional[Dict[str, Any]] = None,
):
    """Log an MCP operation for audit purposes."""
    if not audit_logger:
        return
    
    log_data = {
        "event_type": "mcp_operation",
        "operation": operation,
        "user_id": user.get("id"),
        "user_email": user.get("email"),
        "tenant_id": tenant,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if details:
        log_data["details"] = details
    
    audit_logger.info(log_data)