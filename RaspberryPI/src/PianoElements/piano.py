import board
import neopixel
from typing import Any, List
import threading
from Midi.midiLineObserver import MidiLineObserver, Mode, MidiEvent



class Note:

    def __init__ (self, noteNumber: int, led_index: int = 0) -> None:
        self._noteNumber: int = noteNumber
        self._pressed: bool = False
        self._velocity: int = 0
        self._led_index: int = led_index

class LED:
    
    def __init__ (self, led_index: int, brightness: float, notes: List[Note]):
        self._brightness: float = brightness
        self._led_index: int = led_index
        self._notes: List[Note] = notes
        self._state: bool = False
        self._dissolvenceTime: float = 0.0
        
    def update_led_state(self, state: bool) -> None:
         self._state = state
         
    def isOn(self) -> bool:
        return self._state
    
    def isOff(self) -> bool:
        return not self._state


class Piano(MidiLineObserver):
    
    def __init__ (
        self, 
        note_number: int, 
        neoPixel_number: int, 
        LED_strip_dataPin,
        *,
        start_note: int = 21,
        end_note: int = 108,
        transpose: int = 0,
        brightness: float = 0.2
    ) -> None:
        super().__init__(Mode.WRITE)
        
        
        if note_number < start_note or note_number > end_note:
            raise ValueError("Note number is out of range")
        
        self._buffer_lock = threading.Lock()
        self._settings_lock = threading.Lock()
        self._event_buffer: List[Any] = list()
        self._task_thread: threading.Thread | None = None
        self._run_task: bool = False
        
        
        self._noteNumber: int = note_number
        self._neoPixel_number: int = neoPixel_number
        self._brightness: float = brightness
        self._dataPin = LED_strip_dataPin #board.D18
        self._neopixel = neopixel.NeoPixel(self._dataPin, self._neoPixel_number, brightness=brightness)
        self._transpose: int = transpose
        
        self._PianoNotes: List[Note] = list()
        self._startNode_number: int = start_note
        self._endNode_number: int = end_note
        self._noteOfsset: int = note_number - start_note
        
        for i in range(start_note, end_note + 1, 1):
            self._PianoNotes.append(Note(i))
            
    def __del__(self) -> None:
        self.stop()
        
    def _syncronized(funtion):
        def wrapper(self, *args, **kwargs):
            with self._settings_lock:
                funtion(self, *args, **kwargs)
        return wrapper
    
    def _syncronized_buffer(funtion):
        def wrapper(self, *args, **kwargs):
            with self._buffer_lock:
                funtion(self, *args, **kwargs)
        return wrapper
    
    @_syncronized
    def start(self) -> None:
        if self._task_thread is not None:
            raise RuntimeError("Task already started")
        
        print("Piano Thread started...")
        self._task_thread = threading.Thread(target=self._task_loop)
        self._run_task = True
        self._task_thread.start()
    
    @_syncronized
    def stop(self) -> None:
        if self._task_thread is None:
            return
        
        self._run_task = False
        while self._task_thread.is_alive():
            self._task_thread.join(0.1)
        self._task_thread = None
        print("Piano Thread stopped...")
    
    @_syncronized_buffer
    def add_event(self, event: Any) -> None:
        self._event_buffer.append(event)
    
    @_syncronized_buffer  
    def clear_events(self) -> None:
        self._event_buffer.clear()
    
    def _task_loop(self) -> None:
        self.clear_events()
        while self._run_task:
            # self.update_leds()
            # self._buffer_lock.acquire()
            # for event in self._event_buffer:
            #     self._handle_event(event)
            # self._event_buffer.clear()
            # self._buffer_lock.release()
            # self._neopixel.show() 
            pass 
            
        self.clear_events()
    
    def handleEvent(self, event: MidiEvent) -> None:
        pass
    
     
    def update_leds(self) -> None:
        pass
    
    def setNote(self, note: int) -> None:
        pass
    
    def resetNote(self, note: int) -> None:
        pass