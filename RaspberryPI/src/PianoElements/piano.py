import globalData
import board
import neopixel
from typing import Any, List
import threading
from Midi.eventLineInterface import EventLineInterface
from Midi.eventLine import EventType
from Midi.lineObserver import LineObserver, EventData
from PianoElements.utility import *
import time
from enum import Enum
import logging


class MIDI_COMMANDS(Enum):
    NOTE_ON = 0x09
    NOTE_OFF = 0x08
    POLYPHONIC_AFTERTOUCH = 0x0A
    CONTROL_CHANGE = 0x0B
    PROGRAM_CHANGE = 0x0C
    

class ANIMATION(Enum):
    pass



class Note:

    def __init__ (self) -> None:
        self.pressed: bool = False
        self.velocity: int = 0
        self.LEDs_index: List[int] = list()
        

class LED:
    
    def __init__ (self, index: int):
        self.index: int = index
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
        super().__init__()
        
        
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
        #self._noteOfsset: int = note_number - start_note
        
        #inizializzo le note
        for _ in range(end_note - start_note):
            self._PianoNotes.append(Note())
            
        for i in range(neoPixel_number):
            self._PianoLEDs.append(LED(i))
        
        # octave_offset = note_to_octave(globalData.NOTE_OFFSET)
        # octave_white_note = white_note_of_octave(globalData.NOTE_OFFSET)
        # total_white_note = octave_white_note + octave_offset * globalData.WHITE_NOTE_PER_OCTAVE
        # distance_offset = total_white_note*globalData.PIANO_WHITE_NOTE_LENGHT
        
        
        
        startOffset = 0
        
        for i in range(len(self._PianoNotes)):
            note = i + globalData.NOTE_OFFSET
            octave = note_to_octave(note)
            octave_index = octave_note_number(note)
            isAltered = is_altered(octave_index)
            asNatualNote = to_white_note(octave_index)
            
            startPoint = (octave*globalData.WHITE_NOTE_PER_OCTAVE + asNatualNote)*globalData.PIANO_WHITE_NOTE_LENGHT
            
            if i == 0:
                startOffset = startPoint + globalData.LED_STRIP_OFFSET
                
            
            noteStart: float = startPoint - startOffset + (globalData.BLACK_NOTE_OFFSET_FROM_WHITE_NOTE if isAltered else 0)
            noteEnd:float = noteStart + (globalData.PIANO_BLACK_NOTE_LENGHT if isAltered else globalData.PIANO_WHITE_NOTE_LENGHT)
            limit: float =  0.4#globalData.BLACK_NOTE_OFFSET_FROM_WHITE_NOTE + globalData.PIANO_WHITE_NOTE_LENGHT/3 if isAltered else globalData.PIANO_WHITE_NOTE_LENGHT/3
            
            print(f"Note {note}: startPoint={startPoint} Altered={isAltered} start={noteStart} end={noteEnd}")
            
            for j, led in enumerate(self._PianoLEDs):
                LED_start = globalData.LED_LENGHT * j
                LED_end = LED_start + globalData.LED_LENGHT
                
                # a: bool = noteStart - limit <= (LED_start + globalData.LED_LENGHT/2)  <= noteEnd + limit
                # b: bool = noteStart - limit <= (LED_end - globalData.LED_LENGHT/2) <= noteEnd + limit
                a: bool = noteStart - limit <= (LED_start)  <= noteEnd + limit
                b: bool = noteStart - limit <= (LED_end) <= noteEnd + limit
                
                if a or b:
                    print(f"LED {j}: start={LED_start} end={LED_end} assigned to NOTE {note}")
                    led.Led_Notes.append(self._PianoNotes[i])
                    self._PianoNotes[i].LEDs_index.append(j)
                    
            
    def __del__(self) -> None:
        self.stop()
        
        
    def _syncronized(funtion):
        def wrapper(self, *args, **kwargs):
            with self._settings_lock:
                return funtion(self, *args, **kwargs)
        return wrapper
    
    def _syncronized_buffer(funtion):
        def wrapper(self, *args, **kwargs):
            with self._buffer_lock:
                return funtion(self, *args, **kwargs)
        return wrapper
    
    @_syncronized
    def start(self) -> None:
        if self._task_thread is not None:
            raise RuntimeError("Task already started")
        
        logging.info("Piano started...")

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
        lastUpdate: float = 0.0
        
        while self._run_task:
            
            while len(self._event_buffer) > 0:
                event = self._pop_event_buffer()
                self.processMidiData(event)
                
            if time.time() - lastUpdate > 1/globalData.LED_REFRESH_RATE:
                lastUpdate = time.time()
                self.update_leds()
            
            
        self._clear_events_buffer()
        
    def update_leds(self) -> None:
        #for i, led in enumerate(self._PianoLEDs):
        for led in self._PianoLEDs:
            if led.state:
                turnOff: bool = True
                
                for note in led.Led_Notes:
                    if note.pressed:
                        led.dissolvenceTime = time.time()
                        turnOff = False
                        break
                    
                if turnOff and (time.time() - led.dissolvenceTime > globalData.LED_DISSOLVENCE_TIME):
                    self.turnOff_LED(led)
            # else:
            #     for note in led.Led_Notes:
            #         if note.pressed:
            
                
            #         self._neopixel[i] = (255, 255, 255)
                    
            #         break
            #     else:
                    
                    
        self._neopixel.show()
        #print("heree2")
    
    def handleEvent(self, event: EventData):
        # match event.type:
        #     case EventType.MIDI:
        #         if self._run_task:
        #             self._onMIDI_data_event(event.data[0])
            
        #     case EventType.SETTING_CHANGE:
        #         pass
            
        #     case _ :
        #         pass
        
        print(event)
        if event.eventType == EventType.MIDI:
            if self._run_task:
                self._onMIDI_data_event(event.data[0])
            
        elif event.eventType == EventType.SETTING_CHANGE:
            pass
        
        else:
            pass
    
    
    @_syncronized_buffer
    def _onMIDI_data_event(self, midiData: List[int]) -> None:
        #print("MIDI DATA: ", midiData)
        self._event_buffer.append(midiData)
    
    @_syncronized_buffer  
    def _clear_events_buffer(self) -> None: 
        self._event_buffer.clear()
    
    @_syncronized_buffer     
    def _pop_event_buffer(self) -> List[int]: 
        event = self._event_buffer.pop(0)
        #print("pop: ", event)
        return event
    
    def processMidiData(self, midi: List[int]) -> None:
        

        command = (midi[0] & 0xF0) >> 4
        channel = midi[0] & 0x0F
        print(f"Processing MIDI data: {midi} -> command: 0X{command:02x} channel: 0X{channel:02x}")


        if command == MIDI_COMMANDS.NOTE_ON.value:
            note = midi[1] + self._transpose - globalData.NOTE_OFFSET
            velocity = midi[2]
            
        
            if velocity == 0:
                self.resetNote(note)
            else:
                self.setNote(note, velocity)
                
        elif command == MIDI_COMMANDS.NOTE_OFF.value:
            note = midi[1] + self._transpose - globalData.NOTE_OFFSET
            velocity = midi[2]

            #note = note + self._transpose - globalData.NOTE_OFFSET
            self.resetNote(note)
            
     
    def setNote(self, note_index: int, velocity: int) -> None:
        if note_index < 0 or note_index > len(self._PianoNotes):
            return

        #print(f"Note ON: {note}, Velocity: {velocity}")
        note = self._PianoNotes[note_index]
        note.pressed = True
        note.velocity = velocity
        logging.debug(f"Note {note_index} pressed with velocity {velocity}")
        
        for led_index in note.LEDs_index:
            self.turnOn_LED(self._PianoLEDs[led_index], velocity)
            
        #super().notifyEvent(EventData(note, EventType.NOTE_PRESSED))
    
    
    
    def resetNote(self, note_index: int) -> None:
        if note_index < 0 or note_index > len(self._PianoNotes):
            return
        
        #print(f"Note OFF: {note}")
        note = self._PianoNotes[note_index]
        note.pressed = False
        note.velocity = 0
        logging.debug(f"Note {note_index} reset")
        #super().notifyEvent(EventData(note, EventType.NOTE_RELEASED))
        
    
    def turnOff_LED(self, led: LED) -> None:
        if led is None:
            return
        
        self._neopixel[led.index] = (0, 0, 0)
        led.state = False
        led.dissolvenceTime = 0.0
        logging.debug(f"LED {led.index} turned off")
        

    def turnOn_LED(self, led: LED, velocity: int = 0) -> None:
        if led is None:
            return
        
        color = (255, 0, 0)

        self._neopixel[led.index] = color
        led.state = True
        led.dissolvenceTime = time.time() + globalData.LED_DISSOLVENCE_TIME
        logging.debug(f"LED {led.index} turned on with color {color} and velocity {velocity}")
