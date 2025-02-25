
from Midi.eventLine import EventData, EventLine, EventType
from Midi.lineObserver import LineObserver


class EventLineInterface(LineObserver):
    
    def __init__(self) -> None:
        self._inputLine: EventLine | None = None
        self._outputLine: EventLine | None = None


    
    def setInputLine(self, inputLine: EventLine) -> None:
        if self._inputLine is not None:
            self._inputLine.removeAllEvents(self)
        self._inputLine = inputLine
        
    def setOutputLine(self, outputLine: EventLine) -> None:
        self._outputLine = outputLine
        
    def listenEvent(self, eventType: EventType) -> None:
        if self._inputLine is None: return
        self._inputLine.addObserver(self, eventType)
        
    def ignoreEvent(self, eventType: EventType) -> None:
        if self._inputLine is None: return
        self._inputLine.removeObserver(self, eventType)
    
    def notifyEvent(self, event: EventData) -> bool:
        if self._outputLine is None: 
            print("No output line set")
            return

        self._outputLine.notify(self, event)
        return True
        
    def handleEvent(self, event: EventData):
        pass
    
    @property
    def _InputLine(self) -> EventLine:
        return self._inputLine
    
    @property
    def _OutputLine(self) -> EventLine:
        return self._outputLine
    
    @_InputLine.setter
    def InputLine(self, inputLine: EventLine) -> None:
        self.setInputLine(inputLine)
        
    @_OutputLine.setter
    def OutputLine(self, outputLine: EventLine) -> None:
        self.setOutputLine(outputLine)

        
