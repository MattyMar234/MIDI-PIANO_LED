from enum import Enum, auto
import threading
from typing import Optional
import rtmidi
import time
import mido
import logging

from EventLine.eventLine import EventLine, Event, EventData, LineObserver
from EventLine.eventLineInterface import EventLineInterface
from Utility.multiProcessingWorker import MultiprocessingWorker

class MidiInterface(EventLineInterface, MultiprocessingWorker):
    
    
    def __init__(self, interface_name: Optional[str] = None, sendMidiDataEvent: Optional[Event] = None, reciveMidiDataEvent: Optional[Event] = None) -> None:
        EventLineInterface.__init__(self)
        MultiprocessingWorker.__init__(self, interface_name)

        self._sendMidiDataEvent: Optional[Event] = sendMidiDataEvent
        self._reciveMidiDataEvent: Optional[Event] = reciveMidiDataEvent

        self._loopFunction: Optional[callable] = None
        self._eventHandleFunction: Optional[callable] = None

    def _setLoopFunctions(self, func: callable):
        self._loopFunction = func

    def _setEventHandleFunction(self, func: callable):
        self._eventHandleFunction = func

    def setSendMidiDataEvent(self, midiDataEvent: Event) -> None:
        self._sendMidiDataEvent = midiDataEvent
        
    def setReciveMidiDataEvent(self, midiDataEvent: Event) -> None:
        self._reciveMidiDataEvent = midiDataEvent
        
    def worker_loop_function(self) -> None:
        try:
            if self._loopFunction is not None:
                
                self._loopFunction(self)
              
            else:
                logging.error(f"Midi interface {self._worker_name} has no loop function set.")
                raise Exception("No loop function set.")
        except Exception as e:
            raise e
        finally:   
            self.stop()
            

    def handleEvent(self, event: EventData) -> None:
        if self._eventHandleFunction is not None:
            self._eventHandleFunction(self, event)
        
        