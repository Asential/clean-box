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