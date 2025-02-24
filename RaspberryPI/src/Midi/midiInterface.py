from RaspberryPI.src.Midi.lineObserver import LineObserver, Mode, EventData
from Midi.eventLine import EventLine
from enum import Enum, auto
import threading
import time
from Midi.eventLineInterface import EventLineInterface
import rtmidi
import mido



class MidiInterface(EventLineInterface):
    

    @classmethod
    def getAvailablePorts():
        midiin = rtmidi.MidiIn()
        available_ports = midiin.get_ports()
        return available_ports
    
    def __init__(self, mode: Mode, midiLine: EventLine, interface_name: str = ""):
        super().__init__(mode)
        
        self._mode: MidiInterface.Mode = mode
        self._midiLine = midiLine
        
        self._port: int | None = None
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
        if self._mode == Mode.WRITE:
            self._buffer.append(event)
    
    @_syncronized
    def start(self, port) -> None:
        self._port = port
        
        if self._task_thread != None:
            return
        
        self._run_task = True
        self._task_thread = threading.Thread(target=self._task_loop)
        self._task_thread.start()
    
    @_syncronized   
    def stop(self) -> None:
        if self._task_thread == None:
            return
        
        self._run_task = False
        self._task_thread.join()
        self._task_thread = None
        
    def _task_loop(self) -> None:
        if self._mode == Mode.READ:
            self._read_loop()
        else:
            self._write_loop()
        
                
    def _read_loop(self) -> None:
        print(f"Midi interface {self._interface_name} start reading on port {self._port}")
        
        try:
            midiin = rtmidi.MidiIn()
            midiin.open_port(self._port)
            while self._run_task:
                msg = midiin.get_message()
                if msg:
                    event = EventData(msg)
                    self._midiLine.notify(event)
                else:
                    time.sleep(0.01)
        except Exception as e:
            print(e)
        
        
                
    def _write_loop(self) -> None:
        # with mido.open_output(self._port) as outport:
        #     while self._run_task:
        #         if len(self._buffer) > 0:
        #             msg = self._buffer.pop(0)
        #             outport.send(msg)
        pass