import globalData
import board
import neopixel
from typing import Any, Dict, List, Optional, Tuple, Union
import threading
import time
from enum import Enum
import logging
import multiprocessing

from EventLine.eventLineInterface import EventLineInterface
from EventLine.eventLine import Event, LineObserver, EventData
from PianoElements.utility import *
from Utility.multiProcessingWorker import MultiprocessingWorker


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


class PianoLED(EventLineInterface, MultiprocessingWorker):
    
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
        
        if note_number < start_note or note_number > end_note:
            raise ValueError("Note number is out of range")
        
        EventLineInterface.__init__(self)
        MultiprocessingWorker.__init__(self)

        
        #------ Sincronization variables and buffer ------
        self._settings_lock = threading.Lock()
        self._currentEvent: Optional[EventData] = None
        
        # ------ Events Name -----
        self._eventToFunction: Dict[Event, callable] = {}
        self._MidiDataEvent: Optional[Event] = None
        
        # ------ Piano parametrers ------
        self._noteNumber: int = note_number
        self._neoPixel_number: int = neoPixel_number
        self._dataPin = LED_strip_dataPin #board.D18
        self._neopixel = neopixel.NeoPixel(self._dataPin, self._neoPixel_number, brightness=brightness)
        self._PianoNotes: List[Note] = list()
        self._PianoLEDs: List[LED] = list()
        self._startNode_number: int = start_note
        self._endNode_number: int = end_note
        
        
        # ------ Settings ------
        self._brightness: float = brightness
        self._transpose: int = transpose
        
        # ------ LED Update & Animations ----- 
        self._update_leds: bool = False
        self._fixed_color: Tuple[int, int, int] = (255, 0, 0)
        self.lastUpdate: float = 0.0
        self._notePressed: List[int] = list()
        
        self._keyOption_to_function = {
            "color" : self.setColor,
            "brightness" : self.setBrightness,
            "animation" : self.setAnimation
        }
        
        
        
        

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
        
        
        note = globalData.NOTE_OFFSET
        octave = note_to_octave(note)
        octave_index = octave_note_number(note)
        isAltered = is_altered(octave_index)
        near_white_note_index = white_note_of_octave(octave_index)
        Note_start_offset = (octave*globalData.WHITE_NOTE_PER_OCTAVE + near_white_note_index)*globalData.PIANO_WHITE_NOTE_LENGHT
        
        for i in range(len(self._PianoNotes)):
            note = i + globalData.NOTE_OFFSET
            octave = note_to_octave(note)
            octave_index = octave_note_number(note)
            isAltered = is_altered(octave_index)
            near_white_note_index = white_note_of_octave(octave_index)
            
            positionOffset = (octave*globalData.WHITE_NOTE_PER_OCTAVE + near_white_note_index)*globalData.PIANO_WHITE_NOTE_LENGHT - Note_start_offset
           
            noteStart: float = positionOffset + (globalData.BLACK_NOTE_OFFSET_FROM_WHITE_NOTE if isAltered else 0)
            noteEnd:float = noteStart + (globalData.PIANO_BLACK_NOTE_LENGHT if isAltered else globalData.PIANO_WHITE_NOTE_LENGHT)
            limit: float =  0.4#globalData.BLACK_NOTE_OFFSET_FROM_WHITE_NOTE + globalData.PIANO_WHITE_NOTE_LENGHT/3 if isAltered else globalData.PIANO_WHITE_NOTE_LENGHT/3
            
            #logging.info(f"Note {note} ({i}): [offset={positionOffset} | Altered={isAltered} | start={noteStart} | end={noteEnd} | octave={octave} | octave_index={octave_index}]")

            
            for j, led in enumerate(self._PianoLEDs):
                LED_start = globalData.LED_LENGHT * j
                LED_end = LED_start + globalData.LED_LENGHT
                
                # a: bool = noteStart - limit <= (LED_start + globalData.LED_LENGHT/2)  <= noteEnd + limit
                # b: bool = noteStart - limit <= (LED_end - globalData.LED_LENGHT/2) <= noteEnd + limit
                a: bool = noteStart - limit <= (LED_start)  <= noteEnd + limit
                b: bool = noteStart - limit <= (LED_end) <= noteEnd + limit
                
                if a or b:
                    #logging.info(f"LED {j}: [start={LED_start} | end={LED_end} assigned to NOTE {note}]")
                    led.Led_Notes.append(self._PianoNotes[i])
                    self._PianoNotes[i].LEDs_index.append(j)
            
            #logging.info("")   
            
        for led in self._PianoLEDs:
            self.turnOff_LED(led)
        
    # ---- gestione eventi ----
    def setMidiDataEvent(self, event: Optional[Event]) -> None:
        assert event is None or isinstance(event, Event), "Event must be of type Event or None"
        
        if event is not None and event not in self._eventToFunction:
            self._MidiDataEvent = event
            self._eventToFunction[event.__str__()] = self._onMIDI_data_event
            logging.info(f"Piano-MIDI-Data Event set on event: {event}") 
        
        elif event is None and self._MidiDataEvent is not None:
            del self._eventToFunction[self._MidiDataEvent]
            self._MidiDataEvent = None
            logging.info("MIDI Data Event removed")
    
    
    
        
    def _syncronized(funtion):
        def wrapper(self, *args, **kwargs):
            with self._settings_lock:
                return funtion(self, *args, **kwargs)
        return wrapper
    
    # ---- Funzioni per eventi ----
    
    
    def handleEvent(self, event: EventData):
        logging.debug(f"Piano received event: {event.eventType} from ")
        if event is not None and event.eventType.__str__() in self._eventToFunction:
            self._inputQueue.put(event)
            #self.__call_function_on_event(event)
        else:
            logging.warning(f"Piano received unknown event: {event.eventType} ")
            
  
    async def async_handleEvent(self, event: EventData):
        # logging.debug(f"Piano received event: {event.eventType} from ")
        # if event is not None and event.eventType.__str__() in self._eventToFunction:
        #     self._inputQueue.put(event)
        # else:
        #     logging.warning(f"Piano received unknown event: {event.eventType} ")
        pass
    
    def __call_function_on_event(self, event: EventData) -> None:
        function: callable = self._eventToFunction.get(event.eventType.__str__(), None)
        
        if function is None:
            logging.warning(f"No function found for event: {event.eventType} - <object at{hex(id(event.eventType))}>")
            return
        
        logging.debug(f"Processing event: {event.eventType}")
        function(event)
    
    def worker_loop_function(self) -> None:
        
        
        while True:
            if not self._inputQueue.empty():
                while self._inputQueue.qsize():
                    self.__call_function_on_event(self._inputQueue.get())
            
            if time.time() - self.lastUpdate > 1/globalData.LED_REFRESH_RATE:
                self.lastUpdate = time.time()
                self.update_leds()
                
            else:
                time.sleep(0.005)
            
            
    def _onMIDI_data_event(self, event: EventData) -> None:
        assert isinstance(event.data, tuple), "Event data must be a tuple"
        self.processMidiData(event.data[0])
            
    
        
    def update_leds(self) -> None:
        #for i, led in enumerate(self._PianoLEDs):
        #update: bool = False
        
        #se devo accendere qualche led
        if len(self._notePressed) > 0:
            for note in [self._PianoNotes[i] for i in self._notePressed]:
                for led_index in note.LEDs_index:
                    self.turnOn_LED(self._PianoLEDs[led_index], note.velocity)
                self._notePressed.pop(0)
            self._update_leds = True

        #se devo spegnere qualche led
        for led in self._PianoLEDs:
            if led.state:
                turnOff: bool = True
                
                for note in led.Led_Notes:
                    if note.pressed:
                        led.dissolvenceTime = time.time()
                        turnOff = False
                        break
                    
                if turnOff and (time.time() - led.dissolvenceTime > globalData.LED_DISSOLVENCE_TIME_DEFAULT):
                    self.turnOff_LED(led)
                    self._update_leds = True
            
                    
        if self._update_leds:
            self._neopixel.show()
            self._update_leds = False     
        

    
    def _onSettingChange(self, setting: Dict[str, Any]) -> None:
        logging.debug(f"Setting changed: {setting}")
        
        for key in setting.keys():
            if key not in self._keyOption_to_function:
                logging.warning(f"Setting {key} not recognized")
                continue
            self._keyOption_to_function[key](setting[key])
            

     
    def setBrightness(self, brightness: float) -> None:
        if type(brightness) != float:
            logging.error("Brightness must be a float")
            return
            
        
        self._brightness = brightness
        self._neopixel.brightness = self._brightness
    
    @_syncronized
    def setColor(self, color: Union[Tuple[int, int, int], str, None]) -> None:
        if color is None or (type(color) != tuple and type(color) != str):
            logging.error("Color must be a tuple or a string")
            return
        
        if type(color) == str:
            if not color.startswith("#"):
                logging.error("Color must be a string starting with #")
                return
            
            color = color[1:]
            
            if len(color) != 6:
                logging.error("Color must be a string of 6 characters")
                return
            
           
            color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
   
        else:
            if len(color) != 3:
                logging.error("Color must be a tuple of 3 elements")
                return

            if type(color[0]) != int or type(color[1]) != int or type(color[2]) != int:
                logging.error("Color must be a tuple of 3 integers")
                return

            if color[0] < 0 or color[0] > 255 or color[1] < 0 or color[1] > 255 or color[2] < 0 or color[2] > 255:
                logging.error("Color must be a tuple of 3 integers between 0 and 255")
                return
        
        self._fixed_color = color
        logging.debug(f"Color set to {color}")
    
    @_syncronized
    def setAnimation(self) -> None:
        pass
    
    
    

    def processMidiData(self, midi: List[int]) -> None:
        
        command = (midi[0] & 0xF0) >> 4
        channel = midi[0] & 0x0F
        logging.debug(f"Processing MIDI data: {midi} -> command: 0X{command:02x} channel: 0X{channel:02x}")

            
        if command == MIDI_COMMANDS.NOTE_ON.value:
            note = midi[1] - self._transpose - globalData.NOTE_OFFSET
            velocity = midi[2]
            
            if velocity == 0:
                self.resetNote(note)
            else:
                self.setNote(note, velocity)

        elif command == MIDI_COMMANDS.NOTE_OFF.value:
            note = midi[1] - self._transpose - globalData.NOTE_OFFSET
            velocity = midi[2]

            #note = note + self._transpose - globalData.NOTE_OFFSET
            self.resetNote(note)

        else:
            logging.error(f"MIDI command {command} not handled")
     
    def setNote(self, note_index: int, velocity: int) -> None:
        logging.debug(f"Note {note_index} pressed with velocity {velocity}")
        
        # if note_index < 0 or note_index > len(self._PianoNotes):
        #     return
        
        note = self._PianoNotes[note_index]
        note.pressed = True
        note.velocity = velocity
        self._notePressed.append(note_index)
        
        #print(self._notePressed)
         
        #super().notifyEvent(EventData(note, EventType.NOTE_PRESSED))
    
    
    
    def resetNote(self, note_index: int) -> None:
        logging.debug(f"Note {note_index} released")
        if note_index < 0 or note_index > len(self._PianoNotes):
            return
        
        note = self._PianoNotes[note_index]
        note.pressed = False
        note.velocity = 0
        
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
        
        color = self._fixed_color

        self._neopixel[led.index] = color
        led.state = True
        led.dissolvenceTime = time.time() + globalData.LED_DISSOLVENCE_TIME_DEFAULT
        logging.debug(f"LED {led.index} turned on with color {color} and velocity {velocity}")
