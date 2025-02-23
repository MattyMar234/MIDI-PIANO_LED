from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any

class MidiEvent(Enum):
    NOTE_ON = auto()
    NOTE_OFF = auto()
    CONTROL_CHANGE = auto()

class Mode(Enum):
    READ = auto()
    WRITE = auto()
    
class MidiEvent:
    def __init__(self, data: Any):
        self.data = data

class MidiLineObserver(ABC):
    def __init__(self, mode: Mode):
        self._mode = mode
        
    def isInput(self):
        return self._mode == Mode.READ
    
    def isOutput(self):
        return self._mode == Mode.WRITE
    
    @abstractmethod
    def handleEvent(self, event: MidiEvent):
        pass
    