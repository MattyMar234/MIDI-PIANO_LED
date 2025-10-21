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
    
    class Mode(Enum):
        READ = auto()
        WRITE = auto()

    @classmethod
    def getAvailablePorts():
        midiin = rtmidi.MidiIn()
        available_ports = midiin.get_ports()
        return available_ports
    
    def __init__(self, mode: Mode, interface_name: Optional[str] = None, midi_channel: int = 0, port: Optional[int] = None, sendMidiDataEvent: Optional[Event] = None, reciveMidiDataEvent: Optional[Event] = None) -> None:
        EventLineInterface.__init__(self)
        MultiprocessingWorker.__init__(self, interface_name)

        self._port: Optional[int] = None
        self._mode: MidiInterface.Mode = mode
        self._midi_channel: int = midi_channel
        self._sendMidiDataEvent: Optional[Event] = sendMidiDataEvent
        self._reciveMidiDataEvent: Optional[Event] = reciveMidiDataEvent
        
    def setPort(self, port: int) -> None:
        self._port = port
        
    def setSendMidiDataEvent(self, midiDataEvent: Event) -> None:
        self._sendMidiDataEvent = midiDataEvent
        
    def setReciveMidiDataEvent(self, midiDataEvent: Event) -> None:
        self._reciveMidiDataEvent = midiDataEvent
    
    
    async def async_handleEvent(self, event: EventData):
        pass

    
   
    
        
    def worker_loop_function(self) -> None:
        try:
            if self._mode == MidiInterface.Mode.READ:
                self._read_loop()
            else:
                self._write_loop()
        except Exception as e:
            raise e
        finally:   
            self.stop()
            

    def handleEvent(self, event: EventData) -> None:
        pass
        
        
    def _read_loop(self) -> None:


        #se non so che evento mandare aspetto un po
        while self._sendMidiDataEvent is None or self._port is None:
            if self._port is None:
                logging.warning(f"Midi interface {self._worker_name} has no port set, waiting...")
            if self._sendMidiDataEvent is None:
                logging.warning(f"Midi interface {self._worker_name} has no midiDataEvent set, waiting...")
            time.sleep(0.800)
       
        logging.info(f"Midi interface {self._worker_name} connected to port {self._port}, starting read loop")
        midiin = rtmidi.MidiIn()
        midiin.open_port(self._port)
        msg = None
        
        while self._running.is_set() and self._sendMidiDataEvent is not None:
            
            msg = midiin.get_message()
            
            if msg is not None:
                while msg:
                    self.notifyEvent(EventData(msg, self._sendMidiDataEvent), as_thread=True)
                    msg = midiin.get_message()
            else:
                time.sleep(0.002)
                
        
            
        
        
                
    def _write_loop(self) -> None:
        # with mido.open_output(self._port) as outport:
        #     while self._run_task:
        #         if len(self._buffer) > 0:
        #             msg = self._buffer.pop(0)
        #             outport.send(msg)
        pass