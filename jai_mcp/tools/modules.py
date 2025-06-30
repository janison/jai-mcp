"""Module management tools for Jai platform."""

import logging
from typing import List, Optional, Dict, Any

from ..server import mcp
from ..client import get_client

logger = logging.getLogger("jai-mcp.tools.modules")


@mcp.tool()
async def create_module(
    name: str,
    description: str,
    module_type: str = "qa",
    examples: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
) -> str:
    """Create a new module in the Jai platform.
    
    Args:
        name: Module name (must be unique within the project)
        description: Description of what the module does
        module_type: Type of module ('qa', 'content', 'api', 'custom')
        examples: Optional list of example questions or use cases
        tags: Optional list of tags for categorization
        
    Returns:
        Success message with module ID or error details
    """
    try:
        client = await get_client()
        async with client:
            module_data = {
                "name": name,
                "description": description,
                "type": module_type,
                "examples": examples or [],
                "tags": tags or [],
            }
            
            result = await client.post("/modules", json=module_data)
            module_id = result.get("id")
            
            return f"✅ Module '{name}' created successfully (ID: {module_id})"
            
    except Exception as e:
        logger.error(f"Module creation failed: {str(e)}")
        return f"❌ Failed to create module '{name}': {str(e)}"


@mcp.tool()
async def list_modules(
    project_id: Optional[str] = None,
    module_type: Optional[str] = None,
    limit: int = 20,
) -> str:
    """List modules in the Jai platform.
    
    Args:
        project_id: Optional project ID to filter modules
        module_type: Optional module type to filter by
        limit: Maximum number of modules to return (default: 20)
        
    Returns:
        Formatted list of modules
    """
    try:
        client = await get_client()
        async with client:
            params = {"limit": limit}
            if project_id:
                params["project_id"] = project_id
            if module_type:
                params["type"] = module_type
            
            result = await client.get("/modules", params=params)
            modules = result.get("modules", [])
            total = result.get("total", len(modules))
            
            if not modules:
                return "No modules found matching the criteria."
            
            response = [f"📦 Found {total} modules"]
            response.append("=" * 30)
            
            for module in modules:
                name = module.get("name", "Unknown")
                mod_id = module.get("id", "N/A")
                mod_type = module.get("type", "unknown")
                description = module.get("description", "No description")
                
                response.append(f"\n🔧 {name} (ID: {mod_id})")
                response.append(f"   Type: {mod_type}")
                response.append(f"   Description: {description}")
                
                # Show tags if available
                tags = module.get("tags", [])
                if tags:
                    response.append(f"   Tags: {', '.join(tags)}")
            
            return "\n".join(response)
            
    except Exception as e:
        logger.error(f"Module listing failed: {str(e)}")
        return f"❌ Failed to list modules: {str(e)}"


@mcp.tool()
async def get_module_details(module_id: str) -> str:
    """Get detailed information about a specific module.
    
    Args:
        module_id: The ID of the module to retrieve
        
    Returns:
        Detailed module information
    """
    try:
        client = await get_client()
        async with client:
            result = await client.get(f"/modules/{module_id}")
            
            response = [f"📋 Module Details: {result.get('name', 'Unknown')}"]
            response.append("=" * 40)
            
            # Basic information
            response.append(f"\n🔧 Basic Information:")
            response.append(f"   ID: {result.get('id', 'N/A')}")
            response.append(f"   Name: {result.get('name', 'N/A')}")
            response.append(f"   Type: {result.get('type', 'N/A')}")
            response.append(f"   Description: {result.get('description', 'N/A')}")
            response.append(f"   Status: {result.get('status', 'N/A')}")
            
            # Tags
            tags = result.get("tags", [])
            if tags:
                response.append(f"   Tags: {', '.join(tags)}")
            
            # Examples
            examples = result.get("examples", [])
            if examples:
                response.append(f"\n💡 Examples:")
                for i, example in enumerate(examples[:5], 1):
                    response.append(f"   {i}. {example}")
                if len(examples) > 5:
                    response.append(f"   ... and {len(examples) - 5} more")
            
            # Configuration
            config = result.get("configuration", {})
            if config:
                response.append(f"\n⚙️  Configuration:")
                for key, value in config.items():
                    response.append(f"   {key}: {value}")
            
            # Timestamps
            created_at = result.get("created_at")
            updated_at = result.get("updated_at")
            if created_at:
                response.append(f"\n📅 Created: {created_at}")
            if updated_at:
                response.append(f"📅 Updated: {updated_at}")
            
            return "\n".join(response)
            
    except Exception as e:
        logger.error(f"Module details retrieval failed: {str(e)}")
        return f"❌ Failed to get module details: {str(e)}"


@mcp.tool()
async def update_module(
    module_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    examples: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
) -> str:
    """Update an existing module.
    
    Args:
        module_id: The ID of the module to update
        name: Optional new name for the module
        description: Optional new description
        examples: Optional new list of examples (replaces existing)
        tags: Optional new list of tags (replaces existing)
        
    Returns:
        Success message or error details
    """
    try:
        client = await get_client()
        async with client:
            update_data = {}
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            if examples is not None:
                update_data["examples"] = examples
            if tags is not None:
                update_data["tags"] = tags
            
            if not update_data:
                return "❌ No updates provided. Please specify at least one field to update."
            
            await client.put(f"/modules/{module_id}", json=update_data)
            
            updated_fields = ", ".join(update_data.keys())
            return f"✅ Module {module_id} updated successfully. Updated fields: {updated_fields}"
            
    except Exception as e:
        logger.error(f"Module update failed: {str(e)}")
        return f"❌ Failed to update module {module_id}: {str(e)}"


@mcp.tool()
async def delete_module(module_id: str, confirm: bool = False) -> str:
    """Delete a module from the Jai platform.
    
    Args:
        module_id: The ID of the module to delete
        confirm: Set to True to confirm deletion (safety check)
        
    Returns:
        Success message or error details
    """
    if not confirm:
        return "❌ Deletion requires confirmation. Set confirm=True to proceed. WARNING: This action cannot be undone."
    
    try:
        client = await get_client()
        async with client:
            await client.delete(f"/modules/{module_id}")
            
            return f"✅ Module {module_id} deleted successfully"
            
    except Exception as e:
        logger.error(f"Module deletion failed: {str(e)}")
        return f"❌ Failed to delete module {module_id}: {str(e)}"