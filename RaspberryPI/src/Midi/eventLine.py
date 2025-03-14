from enum import Enum, auto
from typing import Any, Dict, Final, List
from Midi.lineObserver import LineObserver, EventData
import threading
import logging

class EventType(Enum):
    MIDI = auto()
    NOTE_PRESSED = auto()
    NOTE_REALEASED = auto()
    SETTING_CHANGE = auto()
    

class EventData:
    def __init__(self, data: Any, eventType: EventType):
        self.data: Final[any] = data
        self.eventType: Final[EventType] = eventType
        
    def __str__(self):
        return f"Event: {self.eventType} | Data: {self.data}"


class EventLine:
    
    def __init__(self) -> None:
        self._event_obsevers: Dict[EventType, List[LineObserver]] = {}
        for eventType in EventType:
            self._event_obsevers[eventType] = []
        

                
    def addObserver(self, observer: LineObserver, eventType: EventType) -> bool:
        if observer in self._event_obsevers[eventType]:
            return False
        
        self._event_obsevers[eventType].append(observer)
        logging.debug(f"Line: {self} | Observer {observer} added for event: {eventType}") 
        return True
        
    
    def removeObserver(self, observer: LineObserver, eventType: EventType) -> bool:
        if not (observer in self._event_obsevers[eventType]):
            return False
        
        self._event_obsevers[eventType].remove(observer)
        logging.debug(f"Line: {self} | Observer {observer} removed for event: {eventType}")  
        return True
        
    def removeAllEvents(self, observer: LineObserver) -> bool:
        for eventType in EventType:
            self.removeObserver(observer, eventType)
        return True
    
    
    def notify(self, obs, event: EventData) -> bool:
        
        # def _task():
        #     for observer in self._event_obsevers[event.eventType]:
        #         if not(obs is None) and observer == obs:
        #             continue
        #         observer.handleEvent(event)
        try:
            logging.debug(f"Line: {self} | Notifying[{event}]")
            # thread = threading.Thread(target=_task)
            # thread.start()
            for observer in self._event_obsevers[event.eventType]:
                if not(obs is None) and observer == obs:
                    continue
                observer.handleEvent(event)
            return True
        except Exception as e:
            print(e)
            return False

       
        
        