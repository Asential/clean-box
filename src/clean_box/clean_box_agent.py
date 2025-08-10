from typing import Literal
from langchain.chat_models import init_chat_model

from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langgraph.types import Command, interrupt

from clean_box.schemas import State, StateInput, UserPreferences
from clean_box.tools.base import get_tools, get_tools_by_name
from clean_box.tools.prompts import AGENT_TOOLS_PROMPT, MEMORY_UPDATE_INSTRUCTIONS, agent_system_prompt, default_background, default_response_preferences
from clean_box.util import format_email_markdown, format_for_display, parse_email_json
load_dotenv("../.env")


tools = get_tools()
tools_by_name = get_tools_by_name(tools)

llm = init_chat_model("openai:gpt-3.5-turbo-0125", temperature=0.0)
llm_with_tools = llm.bind_tools(tools, tool_choice="any")

def get_memory(store, namespace, default_content=None):
    user_preferences = store.get(namespace, "user_preferences")
    if user_preferences:
        return user_preferences.value
    else: 
        store.put(namespace, "user_preferences", default_content)
        user_preferences = default_content

    return user_preferences
        
def update_memory(store, namespace, messages):
    user_preferences = store.get(namespace, "user_preferences")
    llm = init_chat_model("openai:gpt-3.5-turbo-0125", temperature=0.0).with_structured_output(UserPreferences)
    result = llm.invoke(
        [
            {
                "role": "system", "content":MEMORY_UPDATE_INSTRUCTIONS.format()
             }
        ]
    )
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
                return "interrupt_handler"

def parse_email(state: State) -> State:
    """Parse the email content and return the state."""
    email_content = parse_email_json(state["email_input"])
    update = {
        "email_input": state["email_input"],
        "messages": [{"role": "user", "content": f"Process this email for deletion or labelling:  {email_content}"}],
    }

    return Command(goto="llm_call", update=update)

def interrupt_handler(state: State) -> Command[Literal["llm_call", "__end__"]]:
    
    result = []

    goto = "llm_call"

    for tool_call in state["messages"][-1].tool_calls:
        hitl_tools = ["delete_email", "Question"]
        if tool_call["name"] not in hitl_tools:
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append({"role": "tool", "content": observation, "tool_call_id": tool_call["id"]})
            continue

        email_input = state["email_input"]
        author, to, subject, email_thread = parse_email_json(email_input)
        original_email_markdown = format_email_markdown(subject, author, to, email_thread)

        tool_display = format_for_display(tool_call)
        description = original_email_markdown + tool_display

        if tool_call["name"] == "delete_email":
            config = {
                "allow_ignore": True,
                "allow_response": False,
                "allow_edit": False,
                "allow_accept": True
            }
        elif tool_call["name"] == "Question":
            config = {
                "allow_ignore": True,
                "allow_respond": True,
                "allow_edit": False,
                "allow_accept": False,
            }
        else:
            raise ValueError(f"Invalid tool call: {tool_call['name']}")
        
        request = {
            "action_request": {
                "action": tool_call["name"],
                "args": tool_call["args"]
            },
            "config": config,
            "description": description,
        }

        response = interrupt([request])[0]

        if response["type"] == "accept":
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])    
            result.append({"role": "tool", "content": observation, "tool_call_id": tool_call["id"]})
        elif response["type"] == "ignore":
            if tool_call["name"] == "delete_email":
                result.append({"role": "tool", "content": "User ignored this email. Ignore this email and end the workflow.", "tool_call_id": tool_call["id"]})
                goto = END
            elif tool_call["name"] == "Question":
                result.append({"role": "tool", "content": "User ignored this question. Ignore this email and end the workflow.", "tool_call_id": tool_call["id"]})
                goto = END
            else:
                raise ValueError(f"Invalid tool call: {tool_call['name']}")
        elif response["type"] == "edit":
            tool = tools_by_name[tool_call["name"]]
            edited_args = response["args"]["args"]
            ai_message = state["messages"][-1]
            current_id = tool_call["id"]

            updated_tool_calls = [tc for tc in ai_message.tool_calls if tc["id"] != current_id] + [
                {"type": "tool_call","name": tool_call["name"], "args": edited_args, "id": current_id}
            ]

            # Create a new opy of message with updated tool calls to keep immutability and prevent any sideeffects.
            result.append(ai_message.model_copy(update={"tool_calls": updated_tool_calls}))
            
            # Currently no tool require edits, but can be added in the future.

        elif response["type"] == "response":
            user_feedback = response["args"]
            if tool_call["name"] == "Question":
                result.append({"role": "tool", "content": f"User responded to the question which we can use for any follow up tasks: {user_feedback}", "tool_call_id": tool_call["id"]})
            else:
                raise ValueError(f"Invalid tool call: {tool_call['name']}")
        
        else :
            raise ValueError(f"Invalid response: {response}")
    
    update = {
        "messages": result,
    }
    return Command(goto=goto, update=update)
    


# Bulding the agent
agent_builder = (
    StateGraph(State, input=StateInput)
    .add_node("parse_email", parse_email)
    .add_node("llm_call", llm_call)
    .add_node("interrupt_handler", interrupt_handler)
    .add_edge(START, "parse_email")
    .add_edge("parse_email", "llm_call")
    .add_conditional_edges(
        "llm_call",
        should_continue,
        {
            "interrupt_handler": "interrupt_handler",
            END: END,
        },
    )
) 
agent = agent_builder.compile()