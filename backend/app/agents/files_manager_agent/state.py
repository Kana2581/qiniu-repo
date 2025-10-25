from typing import TypedDict

from langchain.agents import AgentState


class FileAgentState(AgentState):
    base_file_path:str

class ToolState(TypedDict):
    base_file_path:str