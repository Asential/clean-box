from langchain.chat_models import init_chat_model

from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
load_dotenv("../.env")

llm = init_chat_model("openai:gpt-3.1-turbo", temperature=0.0)

