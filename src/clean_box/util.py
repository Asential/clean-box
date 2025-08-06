from typing import Any, List


def parse_email_json(email_input: dict) -> dict:
    return (
        email_input["author"],
        email_input["to"],
        email_input["subject"],
        email_input["email_thread"],
    )

def extract_tool_calls(messages: List[Any]) -> List[dict]:
    """Extract tool calls from the last message in the list."""
    tool_call_names = []
    if not messages:
        return []
    for message in messages:
        if isinstance(message, dict) and message.get("tool_calls"):
            tool_call_names.extend(call["name"].lower() for call in message["tool_calls"])
        elif hasattr(message, "tool_calls") and message.tool_calls:
            tool_call_names.extend([call["name"].lower() for call in message.tool_calls])
    
    return tool_call_names

def format_messages_string(messages: List[Any]) -> str:
    """Format messages into a single string for analysis."""
    return '\n'.join(message.pretty_repr() for message in messages)
