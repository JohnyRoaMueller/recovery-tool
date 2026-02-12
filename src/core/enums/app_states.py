from enum import Enum, auto

class AppState(Enum):
    INTRO = auto()
    FLASH_PREP = auto()
    FLASH_DONE = auto()
    UNLOCK_PREP = auto()
    UNLOCK_DONE = auto()