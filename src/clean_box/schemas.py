from typing import TypedDict
from pydantic import BaseModel, Field
from typing_extensions import Literal
from langgraph.graph import MessagesState

classification_choices = Literal["spam", "important", "useless"]

class State(MessagesState):
    email_input: dict

class StateInput(TypedDict):
    # This is the input to the state
    email_input: dict

class UserPreferences(BaseModel):
    """Updated user preferences based on user's feedback."""
    chain_of_thought: str = Field(description="Reasoning about which user preferences need to add/update if required")
    user_preferences: str = Field(description="Updated user preferences")