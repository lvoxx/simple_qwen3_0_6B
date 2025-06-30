from enum import Enum

class ChatMode(str, Enum):
    THINKING = "Think deeper"
    IMAGE = "Generate image"
    WEB_SEARCH = "Search the web"
    CREATIVE = "Creative writing or coding"
    RESEARCH = "Deep research mode"
    NONE = "None"
