from langchain_core.tools import tool

from backend.app.agents.files_manager_agent.graph import file_agent


from langgraph.types import StreamWriter

# @tool
# async def manage_music(request: str) -> str:
#     """Control and manage music playback using natural language.
#
#     Use this when the user wants to play, pause, skip, or organize music.
#     Handles playlist creation, song search, volume control, and playback state management.
#
#     Input: Natural language music request (e.g., 'play jazz.mp4',
#     'pause the song playing','resume the song playing','stop the song playing')
#     """
#
#     result =await music_agent.ainvoke({
#         "messages": [{"role": "user", "content": request}]
#     })
#     return result["messages"][-1].text


@tool
async def manage_files(request: str) -> str:
    """Manage files and folders using natural language.

    Use this when the user wants to create, move, rename, delete, or search files.
    Handles directory navigation, file metadata retrieval, and file organization.

    Input: Natural language file management request (e.g., 'read x.txt', 'open index.html with os','write some message to summary.txt', 'delete old backups'.eg)
    """

    result =await file_agent.ainvoke({
        "messages": [{"role": "user", "content": request}]
    })
    return result["messages"][-1].text
tools_list=[ manage_files]