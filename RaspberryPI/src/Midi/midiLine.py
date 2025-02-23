from typing import Dict, List
from Midi.midiLineObserver import MidiLineObserver, MidiEvent

class MidiLine:
    
    def __init__(self, observers: List[MidiLineObserver] = []) -> None:
        self._INPUT_observers = []
        self._OUTPUT_observers = []
        self._lineObservers: Dict[MidiLineObserver, bool] = {}
        
        for observer in observers:
            self.addObserver(observer)
                
    def addObserver(self, observer: MidiLineObserver):
        if observer in self._lineObservers:
            return
        
        if observer.isInput():
            self._INPUT_observers.append(observer)
        else:
            self._OUTPUT_observers.append(observer)
        
        print(f"Line {self} observer added: {observer}")   
        self._lineObservers[observer] = 0
    
    def removeObserver(self, observer: MidiLineObserver):
        if not (observer in self._lineObservers):
            return
        
        if observer.isInput():
            self._INPUT_observers.remove(observer)
        else:
            self._OUTPUT_observers.remove(observer)
        
    def notify(self, event: MidiEvent):
        for observer in self._OUTPUT_observers:
            observer.handleEvent(event)
        