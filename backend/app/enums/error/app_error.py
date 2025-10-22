
from enum import Enum

class AppError(Enum):
    MODEL_VALIDATION_FAILED = (
        "E1000",
        "llm initialization failed."
    )
    RESUME_NOT_FOUND = ("E1001", "Resume with the specified ID was not found.")
    DATA_VALIDATION_FAILED = ("E1002", "Data validation failed.")
    INTERNAL_SERVER_ERROR = ("E1003", "Internal server error occurred.")

    SESSION_NOT_FOUND = ("E2001", "Valid chat session not found, session_id: {session_id}")
    SESSION_DATA_INVALID = ("E2002", "Chat session data format error")
    def code(self): return self.value[0]
    def message(self): return self.value[1]