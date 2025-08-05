from typing import Dict, List, Optional
from langchain_core.tools import BaseTool

def get_tools(tool_names: Optional[List[str]] = None) -> List[BaseTool]:
    """Get specified tools or all tools if tool_names is None.
    
    Args:
        tool_names: Optional list of tool names to include. If None, returns all tools.
        
    Returns:
        List of tool objects
    """

    from clean_box.tools.local.email_tools import Done, delete_email, label_email

    # Base tools dictionary
    all_tools = {
        "label_email": label_email,
        "delete_email": delete_email,
        "Done": Done,
    }
   
    if tool_names is None:
        return list(all_tools.values())
    
    return [all_tools[name] for name in tool_names if name in all_tools]

def get_tools_by_name(tools: Optional[List[BaseTool]] = None) -> Dict[str, BaseTool]:
    """Get a dictionary of tools mapped by name."""
    if tools is None:
        tools = get_tools()
    
    return {tool.name: tool for tool in tools}
