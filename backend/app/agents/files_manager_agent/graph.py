import time

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from backend.app.agents.files_manager_agent.tools import tools_list

model=init_chat_model("ollama:gpt-oss:20b",baseurl="http://127.0.0.1:11434")
file_agent = create_agent(
    model=model,
    tools=tools_list,
    system_prompt=(
        "You are a helpful personal assistant. "
        "You can schedule calendar events and send emails. "
        "Break down user requests into appropriate tool calls and coordinate the results. "
        "When a request involves multiple actions, use multiple tools in sequence."
    ),
    name="file_agent",
)
# messages=file_agent.invoke({"messages": [{"role": "user", "content":"创建一个233.txt文件然后写入233，然后再帮我列出所有文件"}]})
# for message in messages["messages"]:
#     print(message)

