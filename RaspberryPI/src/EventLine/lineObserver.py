from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any
import asyncio

from EventLine.eventLine import EventData




class LineObserver(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def handleEvent(self, event: EventData):
        pass
    
    @abstractmethod
    async def async_handleEvent(self, event: EventData):
        pass
    