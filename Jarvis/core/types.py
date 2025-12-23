from enum import Enum

class IntentType(Enum):
    SYSTEM_HELP = "system_help"
    MEMORY_QUERY = "memory_query"
    UNKNOWN = "unknown"