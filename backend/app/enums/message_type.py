
from enum import Enum


class MessageType(str, Enum):
    tool = "tool"
    ai = "ai"
    human = "human"
    system="system"