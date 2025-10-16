from RaspberryPI.src.EventLine.eventLine import EventLine, Event, EventData
from RaspberryPI.src.EventLine.eventLineInterface import EventLineInterface
from RaspberryPI.src.EventLine.lineObserver import LineObserver 
from enum import Enum, auto
import threading
import rtmidi
import time
import mido
import logging



class MidiInterface(EventLineInterface):
    
    class Mode(Enum):
        READ = auto()
        WRITE = auto()

    @classmethod
    def getAvailablePorts():
        midiin = rtmidi.MidiIn()
        available_ports = midiin.get_ports()
        return available_ports
    
    def __init__(self, mode: Mode, interface_name: str = ""):
        super().__init__()


        self._port: int | None = None
        self._mode = mode
        self._lock = threading.Lock()
        self._task_thread: threading.Thread | None = None
        self._run_task: bool = False
        self._buffer = []
        
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
        print(f"Midi interface {self._interface_name} start reading on port {self._port}")
        
        midiin = rtmidi.MidiIn()
        midiin.open_port(self._port)
        while self._run_task:
            msg = midiin.get_message()
            if msg:
                super().notifyEvent(EventData(msg, Event.MIDI))
            else:
                time.sleep(0.01)
        
            
        
        
                
    def _write_loop(self) -> None:
        # with mido.open_output(self._port) as outport:
        #     while self._run_task:
        #         if len(self._buffer) > 0:
        #             msg = self._buffer.pop(0)
        #             outport.send(msg)
        pass