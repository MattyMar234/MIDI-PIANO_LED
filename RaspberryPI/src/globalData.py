from typing import Dict, Final, Generic, TypeVar
from enum import Enum
import os

##===============[SETTINGS FILE]===============##
# CWD: Final[str] = os.getcwd()
# DATA_FOLDER = __file__

##===============[PIANO SETTINGS]===============##
PIANO_PORT_NAME: Final[str] = "Digital Piano"
NOTE_OFFSET: Final[int] = 21
LED_LENGHT: float = 1.65
PIANO_NOTE_LENGHT: float = 2.4
PIANO_WHITE_NOTE_LENGHT: Final[float] = 2.4
PIANO_BLACK_NOTE_LENGHT: Final[float] = 1.2
BLACK_NOTE_OFFSET_FROM_WHITE_NOTE: Final[float] = ((PIANO_WHITE_NOTE_LENGHT/3)*2)
PIANO_TOTAL_WHITE_NOTE: Final[int] = 52
PIANO_TOTAL_BLACK_NOTE: Final[int] = 36
WHITE_NOTE_PER_OCTAVE: Final[int] = 7
PIANO_LENGHT: Final[int] = (PIANO_TOTAL_WHITE_NOTE*PIANO_NOTE_LENGHT)
TOTAL_LED: int = (PIANO_LENGHT/LED_LENGHT)
LED_STRIP_OFFSET: Final[float] = 0.0


LED_REFRESH_RATE: int = 70
LED_DISSOLVENCE_TIME_DEFAULT: Final[float] = 0.160
DEFAULT_BRIGHTNESS_VALUE: Final[float] = 0.4


PIANO_NOTE_NUMBER: Final[int] = 88
PIANO_NOTE_START: Final[int] = 21
NOTE_NUMBER_END: Final[int] = 104





T = TypeVar("T")
class SettingsData(Generic[T]):
    
    def __init__(self, parametreName: str, minValue: T, maxValue: T, value: T) -> None:
        super().__init__()

        self.name: Final[str] = parametreName
        self.minValue: Final[T] = minValue
        self.maxValue: Final[T] = maxValue
        self._value = value

    def setValue(self, newValue: T) -> None:
        if self.minValue <= newValue <= self.maxValue:
            self._value = newValue
            return
        
        raise ValueError("value out of range")

    def jsonData(self) -> Dict[str, any]:
        return {
            "name" : self.name,
            "minValue" : self.minValue,
            "maxValue" : self.maxValue,
            "value" : self._value
        }



class Settings(Enum):
    DISSOLVENZE = SettingsData[float]("Dissolvenze", 0.010, 1, LED_DISSOLVENCE_TIME_DEFAULT)
    BRIGHTNESS = SettingsData[float]("Brightness", 0.0, 1.0, DEFAULT_BRIGHTNESS_VALUE)
    NOTE_SIZE = SettingsData[float]("Note size", 0.0, 3.0, PIANO_WHITE_NOTE_LENGHT)
    #LED_SIZE = 
    


#data = {}

# for i, obj in enumerate(list(Settings)):
#     data[i] = obj.value.jsonData() 

# print(data)

