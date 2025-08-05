from typing import Literal
from pydantic import BaseModel
from langchain_core.tools import tool

@tool
def label_email(label:str) -> str:
    """Add email to a label."""
    return f"Email has been moved to label: {label}"

# [TODO] Can potentially add level of importance of deletion to think on HITL
@tool
def delete_email(sender: str, date: str) -> str:
    """Delete email."""
    return f"Email from {sender} received on {date} has been deleted."

@tool
class Done(BaseModel):
    """E-mail has been processed."""
    done: bool
