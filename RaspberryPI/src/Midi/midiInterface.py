from enum import Enum, auto
import threading
from typing import Optional
import rtmidi
import time
import mido
import logging

from EventLine.eventLine import EventLine, Event, EventData, LineObserver
from EventLine.eventLineInterface import EventLineInterface

class MidiInterface(EventLineInterface):
    
    class Mode(Enum):
        READ = auto()
        WRITE = auto()

    @classmethod
    def getAvailablePorts():
        midiin = rtmidi.MidiIn()
        available_ports = midiin.get_ports()
        return available_ports
    
    def __init__(self, mode: Mode, interface_name: str = "", midi_channel: int = 0, midiDataEvent: Optional[Event] = None) -> None:
        super().__init__()


        self._port: int | None = None
        self._mode = mode
        self._lock = threading.Lock()
        self._task_thread: threading.Thread | None = None
        self._run_task: bool = False
        self._buffer = []
        self._midi_channel = midi_channel
        self._midiDataEvent = midiDataEvent
        
         # ------ Interface Name -----
        
        if interface_name == "":
            interface_name = self.__hash__()
    
        self._interface_name = interface_name
    
    
    def _syncronized(funtion):
        def wrapper(self, *args, **kwargs):
            with self._lock:
                funtion(self, *args, **kwargs)
        return wrapper 
   
    
    def handleEvent(self, event: EventData) -> None:
        if self._mode == MidiInterface.Mode.WRITE:
            self._buffer.append(event)
    
    async def async_handleEvent(self, event: EventData):
        pass
    
    def isRunning(self) -> bool:
        return self._task_thread != None
    
    @_syncronized
    def start(self, port) -> None:
        self._port = port
        
        if self._task_thread != None:
            return
        
        try:
            self._run_task = True
            self._task_thread = threading.Thread(target=self._task_loop)
            self._task_thread.start()
        except Exception as e:
            self._run_task = False
            self._task_thread = None
        
    @_syncronized   
    def stop(self) -> None:
        if self._task_thread == None:
            return
        
        self._run_task = False
        try:
            self._task_thread.join(2.0)
        except Exception as e:
            logging.error(e)
        self._task_thread = None
        
    def _task_loop(self) -> None:
        try:
            if self._mode == MidiInterface.Mode.READ:
                self._read_loop()
            else:
                self._write_loop()
        except Exception as e:
            logging.error(e)
        finally:   
            self.stop()
        
        
    def _read_loop(self) -> None:
        logging.info(f"Midi interface {self._interface_name} start reading on port {self._port}")
        
        midiin = rtmidi.MidiIn()
        midiin.open_port(self._port)
        msg = None
        
        while self._run_task:
            
            if self._midiDataEvent is None:
                time.sleep(0.200)
                continue
            
            msg = midiin.get_message()
            
            if msg is not None:
                while msg:
                    self.notifyEvent(EventData(msg, self._midiDataEvent), as_thread=True)
                    msg = midiin.get_message()
            else:
                time.sleep(0.001)
                
        
            
        
        
                
    def _write_loop(self) -> None:
        # with mido.open_output(self._port) as outport:
        #     while self._run_task:
        #         if len(self._buffer) > 0:
        #             msg = self._buffer.pop(0)
        #             outport.send(msg)
        pass