import globalData
import digitalio
try:    
    import board
except:
    print("Libreria board diposnibile")
    board = None

    

from typing import Any, Dict, Final, List, Optional, Tuple, Union
import threading
import time
from enum import Enum, auto
import logging

from EventLine.eventLineInterface import EventLineInterface
from EventLine.eventLine import Event, LineObserver, EventData
from PianoElements.utility import *
from Utility.multiProcessingWorker import MultiprocessingWorker



class Pedal(EventLineInterface, MultiprocessingWorker):

    def __init__(self) -> None:
        self._Pin = None

    
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
            


class PedalFactory:

    class PedalMode(Enum):
        RESING = auto()
        FALLING = auto()
        CHANGE = auto()

    class PullMode(Enum):
        NONE = auto()
        PULL_UP = auto()
        PULL_DOWN = auto()

    def __init__(self) -> None:
        pass

    @staticmethod
    def makePedalObject(GPIO, mode: PedalMode=PedalMode.FALLING, pullMode: PullMode = PullMode.NONE, bouncetime: int = 100) -> Pedal:
        GPIO.setmode(GPIO.BCM)
        PIN = board.D18.id 

        if  pullMode == PedalFactory.PullMode.PULL_UP:
            GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        elif pullMode == PedalFactory.PullMode.PULL_UP:
            GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        else:
            GPIO.setup(PIN, GPIO.IN)

        pedal = Pedal()
        pedal._Pin = PIN

        
        if pullMode == PedalFactory.PedalMode.RESING:
        GPIO.add_event_detect(PIN, GPIO.FALLING, callback=on_event, bouncetime=200)

        elif pullMode == PedalFactory.PedalMode.RESING:



        pin = digitalio.DigitalInOut(board.D18)
        pin.direction = digitalio.Direction.INPUT
        pin.pull = digitalio.Pull.UP  # oppure Pull.DOWN, a seconda del circuito



