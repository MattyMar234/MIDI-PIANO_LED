from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any

class EventData(Enum):
    NOTE_ON = auto()
    NOTE_OFF = auto()
    CONTROL_CHANGE = auto()


    


class LineObserver(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def handleEvent(self, event: EventData):
        pass
    