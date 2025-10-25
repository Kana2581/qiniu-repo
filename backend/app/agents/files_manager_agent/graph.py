import time
from datetime import datetime

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from backend.app.agents.files_manager_agent.state import FileAgentState
from backend.app.agents.files_manager_agent.tools import tools_list

# system_prompt = (
#     "You are a helpful personal assistant. "
#     "You can schedule calendar events and send emails. "
#     "Break down user requests into appropriate tool calls and coordinate the results. "
#     "When a request involves multiple actions, use multiple tools in sequence."
# ),
def get_file_agent(prompt_text:str,model_name:str,provider:str,system_type:str,base_url:str=None,api_key:str=None):
    model=init_chat_model(model=model_name,model_provider=provider,baseurl=base_url,api_key=api_key)
    return create_agent(
        model=model,
        tools=tools_list,
        system_prompt=(
            f"{prompt_text}"
            "Before making any tool calls, first explain clearly why the tool is needed and how it helps address the user’s request. Then, break down the user’s request into appropriate tool calls, execute them in a logical order, and coordinate their results to produce a coherent final answer. "
            "When a request involves multiple actions, use multiple tools in sequence."
            f"The current date and time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
            f"This os is {system_type}"
        ),
        name="file_agent",
        state_schema=FileAgentState
    )
# messages=file_agent.invoke({"messages": [{"role": "user", "content":"创建一个233.txt文件然后写入233，然后再帮我列出所有文件"}]})
# for message in messages["messages"]:
#     print(message)

