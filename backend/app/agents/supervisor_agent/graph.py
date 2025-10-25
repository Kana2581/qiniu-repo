import asyncio

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage



from backend.app.utils.agent_util import base_message2chat_messages_base

model=init_chat_model("ollama:gpt-oss:20b",baseurl="http://127.0.0.1:11434")
supervisor_agent = create_agent(
    model,

    system_prompt=(
        "You are a helpful personal assistant. "
        "You can schedule calendar events and send emails. "
        "Break down user requests into appropriate tool calls and coordinate the results. "
        "When a request involves multiple actions, use multiple tools in sequence."
    ),


)

messages=supervisor_agent.ainvoke({"messages": [{"role": "user", "content":"你可以写一个关于蜘蛛的冒险小说并写到蜘蛛冒险故事.txt文件里"}]})
messages=asyncio.run(messages)
for message in messages["messages","updates"]:
    print(message)

