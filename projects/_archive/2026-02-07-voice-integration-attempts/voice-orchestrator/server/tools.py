"""
Tool definitions and execution for voice agent
"""

import json
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


# Tool definitions in OpenAI format
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_kitchen_inventory",
            "description": "Check what ingredients are in the kitchen (pantry, fridge, freezer)",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "enum": ["all", "pantry", "fridge", "freezer"],
                        "description": "Which location to check"
                    }
                },
                "required": []
            }
        }
    }
]


async def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> str:
    """
    Execute a tool and return the result as a string
    
    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments for the tool
        
    Returns:
        String result to inject back into conversation
    """
    try:
        logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
        
        if tool_name == "get_kitchen_inventory":
            return await get_kitchen_inventory(tool_args.get("location", "all"))
        
        else:
            return f"Unknown tool: {tool_name}"
            
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
        return f"Error executing {tool_name}: {str(e)}"


async def get_kitchen_inventory(location: str = "all") -> str:
    """Get kitchen inventory from pantry.yaml"""
    try:
        workspace = Path.home() / ".openclaw" / "workspace"
        pantry_file = workspace / "kitchen" / "pantry.yaml"
        
        if not pantry_file.exists():
            return "Kitchen inventory system not set up yet."
        
        with open(pantry_file) as f:
            pantry_data = yaml.safe_load(f)
        
        if not pantry_data:
            return "Kitchen inventory is empty."
        
        # Build response based on location
        results = []
        
        if location == "all" or location == "pantry":
            pantry_items = pantry_data.get("pantry", {})
            if pantry_items:
                items_list = [f"{item['quantity']} {item['name']}" for item in pantry_items]
                results.append(f"Pantry: {', '.join(items_list)}")
        
        if location == "all" or location == "fridge":
            fridge_items = pantry_data.get("fridge", {})
            if fridge_items:
                items_list = [f"{item['quantity']} {item['name']}" for item in fridge_items]
                results.append(f"Fridge: {', '.join(items_list)}")
        
        if location == "all" or location == "freezer":
            freezer_items = pantry_data.get("freezer", {})
            if freezer_items:
                items_list = [f"{item['quantity']} {item['name']}" for item in freezer_items]
                results.append(f"Freezer: {', '.join(items_list)}")
        
        if results:
            return ". ".join(results)
        else:
            return f"No items found in {location}."
            
    except Exception as e:
        logger.error(f"Error reading kitchen inventory: {e}", exc_info=True)
        return f"Error checking kitchen inventory: {str(e)}"
