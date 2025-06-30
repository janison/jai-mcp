"""Health monitoring tools for Jai platform."""

import logging
from typing import Optional

from ..server import mcp
from ..client import get_client

logger = logging.getLogger("jai-mcp.tools.health")


@mcp.tool()
async def check_platform_health(detailed: bool = False) -> str:
    """Check the overall health of the Jai platform.
    
    Args:
        detailed: If True, returns detailed health information for all components
        
    Returns:
        Health status summary or detailed report
    """
    try:
        client = await get_client()
        async with client:
            health_data = await client.health_check()
            
            if not detailed:
                status = health_data.get("status", "unknown")
                return f"Platform Status: {status.upper()}"
            
            # Detailed health information
            result = ["🏥 Jai Platform Health Report"]
            result.append("=" * 40)
            
            # Overall status
            overall_status = health_data.get("status", "unknown")
            emoji = "✅" if overall_status == "healthy" else "❌"
            result.append(f"\n{emoji} Overall Status: {overall_status.upper()}")
            
            # Component statuses
            components = health_data.get("components", {})
            if components:
                result.append("\n📊 Component Status:")
                for name, component in components.items():
                    status = component.get("status", "unknown")
                    emoji = "✅" if status == "healthy" else "❌"
                    result.append(f"  {emoji} {name}: {status}")
                    
                    # Add metrics if available
                    metrics = component.get("metrics", {})
                    if metrics:
                        for key, value in metrics.items():
                            result.append(f"    • {key}: {value}")
            
            # Timestamp
            timestamp = health_data.get("timestamp")
            if timestamp:
                result.append(f"\n🕐 Last Updated: {timestamp}")
            
            return "\n".join(result)
            
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return f"❌ Health check failed: {str(e)}"


@mcp.tool()
async def check_api_endpoints() -> str:
    """Test connectivity to key API endpoints.
    
    Returns:
        Status of API endpoint connectivity
    """
    try:
        client = await get_client()
        async with client:
            # Test basic connectivity
            await client.health_check()
            
            return "✅ API endpoints are accessible"
            
    except Exception as e:
        logger.error(f"API endpoint check failed: {str(e)}")
        return f"❌ API endpoints unreachable: {str(e)}"


@mcp.tool()
async def get_platform_metrics() -> str:
    """Retrieve platform usage metrics and statistics.
    
    Returns:
        Formatted metrics report
    """
    try:
        client = await get_client()
        async with client:
            metrics_data = await client.get("/metrics")
            
            result = ["📊 Platform Metrics"]
            result.append("=" * 30)
            
            # Usage statistics
            usage = metrics_data.get("usage", {})
            if usage:
                result.append("\n📈 Usage Statistics:")
                result.append(f"  • Active Users: {usage.get('active_users', 'N/A')}")
                result.append(f"  • Total Modules: {usage.get('total_modules', 'N/A')}")
                result.append(f"  • Total Projects: {usage.get('total_projects', 'N/A')}")
                result.append(f"  • API Requests (24h): {usage.get('api_requests_24h', 'N/A')}")
            
            # Performance metrics
            performance = metrics_data.get("performance", {})
            if performance:
                result.append("\n⚡ Performance Metrics:")
                result.append(f"  • Average Response Time: {performance.get('avg_response_time', 'N/A')}ms")
                result.append(f"  • Success Rate: {performance.get('success_rate', 'N/A')}%")
                result.append(f"  • Error Rate: {performance.get('error_rate', 'N/A')}%")
            
            return "\n".join(result)
            
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {str(e)}")
        return f"❌ Unable to retrieve metrics: {str(e)}"