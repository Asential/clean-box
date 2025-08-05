from typing import Literal
from langchain.chat_models import init_chat_model

from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langgraph.types import Command

from clean_box.schemas import State, StateInput
from clean_box.tools.base import get_tools, get_tools_by_name
from clean_box.tools.prompts import AGENT_TOOLS_PROMPT, agent_system_prompt, default_background, default_response_preferences
from clean_box.util import parse_email_json
load_dotenv("../.env")


tools = get_tools()
tools_by_name = get_tools_by_name(tools)

llm = init_chat_model("openai:gpt-3.5-turbo-0125", temperature=0.0)
llm_with_tools = llm.bind_tools(tools, tool_choice="any")

# Nodes
def llm_call(state: State):
    """Basic LLM to classify the email."""

    return {
        "messages": [
            llm_with_tools.invoke(
                [
                    {"role": "system", "content": agent_system_prompt.format(
                        tools_prompt=AGENT_TOOLS_PROMPT,
                        background=default_background,
                        response_preferences=default_response_preferences, 
                        )
                    },
                    
                ]
                + state["messages"]
            )
        ]
    }

def tool_node(state: State):
    """Performs the tool call"""

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append({"role": "tool", "content" : observation, "tool_call_id": tool_call["id"]})
    return {"messages": result}

# Conditional edge function
def should_continue(state: State) -> Literal["Action", "__end__"]:
    """Route to Action, or end if Done tool called"""
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        for tool_call in last_message.tool_calls: 
            if tool_call["name"] == "Done":
                return END
            else:
                return "Action"

def parse_email(state: State) -> State:
    """Parse the email content and return the state."""
    # Here you can add logic to parse the email content
    # For now, we just return the state as is
    email_content = parse_email_json(state["email_input"])
    update = {
        "email_input": email_content,
        "messages": [{"role": "user", "content": f"Classify this email  {email_content}"}],
    }

    return Command(goto="llm_call", update=update)

# Bulding the agent
agent_builder = (
    StateGraph(State, input=StateInput)
    .add_node("parse_email", parse_email)
    .add_node("llm_call", llm_call)
    .add_node("environment", tool_node)
    .add_edge(START, "parse_email")
    .add_edge("parse_email", "llm_call")
    .add_conditional_edges(
        "llm_call",
        should_continue,
        {
            "Action": "environment",
            END: END,
        },
    )
    .add_edge("environment", "llm_call")
) 
agent = agent_builder.compile()