import asyncio
from enum import Enum, auto
from typing import Any, Dict, Final, List
from RaspberryPI.src.EventLine.lineObserver import LineObserver
import threading
import logging


    

class Event:
    
    def __init__(self, name: str, observers: List[LineObserver] = []) -> None:
        self.__name: Final[str] = name
        self.__observers: List[LineObserver] = observers


class EventData:
    
    def __init__(self, data: Any, event: Event):
        self.data: Final[Any] = data
        self.eventType: Final[Event] = event
        
    def __str__(self):
        return f"Event: {self.eventType} | Data: {self.data}"


class EventFactory:
    
    __EventTypeCache: Dict[str, Event] = {}
    
    @staticmethod
    def createEventType(name: str) -> Event:
        if name in EventFactory.__EventTypeCache:
            raise ValueError(f"EventType {name} already exists")
        
        name = name.upper()
        return Event(name, [])
    
    @staticmethod
    def getEventType(name: str) -> Event | None:
        return EventFactory.__EventTypeCache[name.upper()]




class EventLine:
    
    def __init__(self) -> None:
        self._event_obsevers: Dict[Event, List[LineObserver]] = {}
    
    def getAvailableEvents(self) -> List[Event]:
        return list(self._event_obsevers.keys())
    
    def registerEvent(self, eventName: Event) -> bool:
        if eventName in self._event_obsevers:
            return False
        
        self._event_obsevers[eventName] = []
        logging.debug(f"Line: {self} | Event {eventName} registered") 
        return True
    
    def unregisterEvent(self, event: Event) -> bool:  
        if not (event in self._event_obsevers):
            return False
        
        for observer in self._event_obsevers[event]:
            if not self.removeObserver(observer, event):
                logging.error(f"Line: {self} | Failed to remove observer {observer} from event {event} during event unregistration")
                return False
            
        self._event_obsevers.pop(event)
        logging.debug(f"Line: {self} | Event {event} unregistered") 
        return True
    

    def __checkEventExists(self, observer: LineObserver, event: Event):
        if not (event in self._event_obsevers):
            logging.error(f"Line: {self} | Event {event} not registered. Cannot add observer {observer}")
            raise ValueError(f"Event {event} not registered in line {self}")
        
  
    def addObserver(self, observer: LineObserver, event: Event) -> bool:
        self.__checkEventExists(observer, event)
        if observer in self._event_obsevers[event]:
            return False
        
        self._event_obsevers[event].append(observer)
        logging.debug(f"Line: {self} | Observer {observer} added for event: {event}") 
        return True
        
    
    def removeObserver(self, observer: LineObserver, event: Event) -> bool:
        self.__checkEventExists(observer, event)
        if not (observer in self._event_obsevers[event]):
            return False
        
        self._event_obsevers[event].remove(observer)
        logging.debug(f"Line: {self} | Observer {observer} removed for event: {event}")  
        return True
        
    def removeAllObserverEvents(self, observer: LineObserver) -> bool:
        for event in self._event_obsevers:
            if observer in self._event_obsevers[event]:
                if not self.removeObserver(observer, event):
                    logging.error(f"Line: {self} | Failed to remove observer {observer} from event {event} during removeAllObserverEvents")
                    return False
        
        return True
    
    
    def notify(self, obs, event: EventData) -> bool:
         
        try:
            logging.debug(f"Line: {self} | Notifying[{event}]")
            for observer in self._event_obsevers[event.eventType]:
                if not(obs is None) and observer == obs:
                    continue
                observer.handleEvent(event)
            return True
        except Exception as e:
            logging.error(e)
            return False
        
    async def async_notify(self, obs, event: EventData, only_async_func: bool = False) -> bool:
        try:
            observers = self._event_obsevers.get(event.eventType, [])

            tasks = [
                s.handleEvent(event) if asyncio.iscoroutinefunction(s.handleEvent) 
                else asyncio.to_thread(s.handleEvent, event)
                for s in observers
                if (asyncio.iscoroutinefunction(s.handleEvent) or not only_async_func) and s != obs
            ]

            if tasks:
                await asyncio.gather(*tasks)

            return True

        except Exception as e:
            logging.error("Errore in Async_notify: %s", e, exc_info=True)
            return False
            
        