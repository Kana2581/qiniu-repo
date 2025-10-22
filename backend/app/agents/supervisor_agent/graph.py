import asyncio

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage

from backend.app.agents.supervisor_agent.tools import tools_list

from backend.app.utils.agent_util import base_message2chat_messages_base

model=init_chat_model("ollama:gpt-oss:20b",baseurl="http://127.0.0.1:11434")
supervisor_agent = create_agent(
    model,
    tools=tools_list,
    system_prompt=(
        "You are a helpful personal assistant. "
        "You can schedule calendar events and send emails. "
        "Break down user requests into appropriate tool calls and coordinate the results. "
        "When a request involves multiple actions, use multiple tools in sequence."
    ),


)

# messages=supervisor_agent.ainvoke({"messages": [{"role": "user", "content":"你可以写一个关于蜘蛛的冒险小说并写到蜘蛛冒险故事.txt文件里"}]})
# messages=asyncio.run(messages)
# for message in messages["messages"]:
#     print(message)

async def main():
        supervisor_agent = create_agent(
            model,
            tools=tools_list,
            system_prompt=(
                "You are a helpful personal assistant. "
                "You can schedule calendar events and send emails. "
                "Break down user requests into appropriate tool calls and coordinate the results. "
                "When a request involves multiple actions, use multiple tools in sequence."
            ),
        )
        li=[]
        async for message in supervisor_agent.astream(
            {"messages": [HumanMessage(content='hello', additional_kwargs={}, response_metadata={}, id='string1'), AIMessage(content='', additional_kwargs={}, response_metadata={}, id='lc_run--0ced18bf-13f1-489f-92db-87e2ea9e5422-0'), HumanMessage(content='hello 你是谁', additional_kwargs={}, response_metadata={}, id='string2')]},
            stream_mode="updates"
        ):
            print(message)
            li.append(message['model']['messages'][-1])

        print(base_message2chat_messages_base(li))





# 用 asyncio.run 启动异步函数
if __name__ == "__main__":

    asyncio.run(main())

    #time.sleep(12000)
# async for message in supervisor_agent.astream({"messages": [{"role": "user", "content":"你可以写一个关于蜘蛛的冒险小说并写到蜘蛛冒险故事.txt文件里"}]},stream_mode="custom"):
#     print(message)
#time.sleep(1000)