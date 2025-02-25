from RaspberryPI.src.Midi.eventLine import EventType
from . import globalData
from Midi.eventLineInterface import EventLineInterface
import board
import neopixel
from typing import Any, List
import threading
from Midi.lineObserver import LineObserver, Mode, EventData
from PianoElements.utility import *


class Note:

    def __init__ (self) -> None:
        self.pressed: bool = False
        self.velocity: int = 0
        

class LED:
    
    def __init__ (self):
        self.brightness: float = 0.0
        #self._led_index: int = led_index
        self.state: bool = False
        self.dissolvenceTime: float = 0.0
        self.Led_Notes: List[Note] = list()

        
    def update_led_state(self, state: bool) -> None:
         self._state = state
         
    def isOn(self) -> bool:
        return self._state
    
    def isOff(self) -> bool:
        return not self._state


class Piano(EventLineInterface):
    
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
        self._event_buffer: List[int] = list()
        self._task_thread: threading.Thread | None = None
        self._run_task: bool = False
        
        
        self._noteNumber: int = note_number
        self._neoPixel_number: int = neoPixel_number
        self._brightness: float = brightness
        self._dataPin = LED_strip_dataPin #board.D18
        self._neopixel = neopixel.NeoPixel(self._dataPin, self._neoPixel_number, brightness=brightness)
        self._transpose: int = transpose
        
        self._PianoNotes: List[Note] = list()
        self._PianoLEDs: List[LED] = list()
        self._startNode_number: int = start_note
        self._endNode_number: int = end_note
        self._noteOfsset: int = note_number - start_note
        
        #inizializzo le note
        for _ in range(end_note - start_note):
            self._PianoNotes.append(Note())
            
        for _ in range(neoPixel_number):
            self._PianoLEDs.append(LED())
        
        octave_offset = note_to_octave(globalData.NOTE_OFFSET)
        octave_white_note = white_note_of_octave(globalData.NOTE_OFFSET)
        total_white_note = octave_white_note + octave_offset * globalData.WHITE_NOTE_PER_OCTAVE
        distance_offset = total_white_note*globalData.PIANO_WHITE_NOTE_LENGHT
        
        for i in range(len(self._PianoNotes)):
            note = i + globalData.NOTE_OFFSET
            octave = note_to_octave(note)
            octave_index = octave_note_number(note)
            isAltered = is_altered(note)
            asNatualNote = to_white_note(note)
            
            st = (octave*globalData.WHITE_NOTE_PER_OCTAVE + asNatualNote)*globalData.PIANO_WHITE_NOTE_LENGHT
            st -= distance_offset
            
            noteStart: float = st + (globalData.BLACK_NOTE_OFFSET_FROM_WHITE_NOTE if isAltered else 0)
            noteEnd:float = noteStart + (globalData.BLACK_NOTE_LENGHT if isAltered else globalData.WHITE_NOTE_LENGHT)
            limit: float =  globalData.BLACK_NOTE_OFFSET_FROM_WHITE_NOTE + globalData.PIANO_WHITE_NOTE_LENGHT/3 if isAltered else globalData.PIANO_WHITE_NOTE_LENGHT/3
            
            for j, led in enumerate(self._PianoLEDs):
                LED_start = globalData.LED_SIZE * j
                LED_end = LED_start + globalData.LED_SIZE
                
                a: bool = noteStart - limit <= LED_start <= noteEnd + limit
                b: bool = noteStart - limit <= LED_end <= noteEnd + limit
                
                if a or b:
                    led.Led_Notes.append(self._PianoNotes[i])
                    
            
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
    
    
    def _task_loop(self) -> None:
        self._clear_events_buffer()
        while self._run_task:
            
            while self._event_buffer > 0:
                event = self._pop_event_buffer()
                self._handle_event(event)
            
            
            
        self._clear_events_buffer()
    
    def handleEvent(self, event: EventData):
        match event.type:
            case EventType.MIDI:
                if self._run_task:
                    self._onMIDI_data_event(event.data[0])
            
            case EventType.SETTING_CHANGE:
                pass
            
            case _ :
                pass
    
    
    @_syncronized_buffer
    def _onMIDI_data_event(self, midiData: List[int]) -> None:
        self._event_buffer.append(midiData)
    
    @_syncronized_buffer  
    def _clear_events_buffer(self) -> None: 
        self._event_buffer.clear()
    
    @_syncronized_buffer     
    def _pop_event_buffer(self) -> List[int]: 
        return self._event_buffer.pop(0)
    
    def processMidiData(self, data: List[int]) -> None:
        print(f"Processing MIDI data: {data}")
     
    def update_leds(self) -> None:
        pass
    
    def setNote(self, note: int) -> None:
        pass
    
    def resetNote(self, note: int) -> None:
        pass