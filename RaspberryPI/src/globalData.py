
from typing import Final


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
LED_DISSOLVENCE_TIME: float = 0.200

PIANO_NOTE_NUMBER: Final[int] = 88
PIANO_NOTE_START: Final[int] = 21
NOTE_NUMBER_END: Final[int] = 104