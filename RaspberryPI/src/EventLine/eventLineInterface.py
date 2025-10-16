
import asyncio
import logging
from EventLine.eventLine import EventData, EventLine, Event
from EventLine.lineObserver import LineObserver


class EventLineInterface(LineObserver):
    
    def __init__(self) -> None:
        # self._inputLine: EventLine | None = None
        # self._outputLine: EventLine | None = None
        
        self._inputLines: list[EventLine] = []
        self._outputLines: list[EventLine] = []

     # --------------------------
    # GESTIONE LINEE
    # --------------------------

    def addLine(self, line: EventLine, direction: str = "input") -> None:
        """Aggiunge una linea di input o output."""
        if direction == "input":
            if line not in self._inputLines:
                self._inputLines.append(line)
        elif direction == "output":
            if line not in self._outputLines:
                self._outputLines.append(line)
        else:
            raise ValueError("direction deve essere 'input' o 'output'")

    def removeLine(self, line: EventLine, direction: str = "input") -> None:
        """Rimuove una linea di input o output.  
        Se è una linea di input, rimuove anche l’observer da tutti gli eventi."""
        if direction == "input":
            if line in self._inputLines:
                try:
                    line.removeAllObserverEvents(self)
                except Exception as e:
                    logging.error("Errore rimuovendo observer dagli eventi: %s", e)
                self._inputLines.remove(line)

        elif direction == "output":
            if line in self._outputLines:
                self._outputLines.remove(line)
        else:
            raise ValueError("direction deve essere 'input' o 'output'")

    # --------------------------
    # FUNZIONI EVENTI
    # --------------------------
    
    def listenEvent(self, event: Event,  line: EventLine) -> None:
        """Registra l'interfaccia come observer di un certo evento su tutte le linee di input."""
        # if self._inputLine is None: return
        # self._inputLine.addObserver(self, eventType)
        for line in self._inputLines:
            if event in line.getAvailableEvents():
                line.addObserver(self, event)
        
    def ignoreEvent(self, event: Event, line: EventLine) -> None:
        # if self._inputLine is None: return
        # self._inputLine.removeObserver(self, eventType)
        
        for line in self._inputLines:
            if event in line.getAvailableEvents():
                line.removeObserver(self, event)
    
    def notifyEvent(self, event: EventData) -> bool:
        """Invia un evento a tutte le linee di output in modo sincrono."""
        if not self._outputLines:
            logging.error("Nessuna linea di output impostata")
            return False

        for line in self._outputLines:
            line.notify(self, event)
        return True
    
    def asyncronous_notifyEvent(self, event: EventData) -> bool:
        """Invia un evento a tutte le linee di output in modo asincrono."""
        if not self._outputLines:
            logging.error("Nessuna linea di output impostata")
            return False

        for line in self._outputLines:
            asyncio.create_task(line.async_notify(self, event))
        return True
    
    
    # --------------------------
    # PROPRIETÀ
    # --------------------------   
    
    @property
    def InputLines(self) -> list[EventLine]:
        return self._inputLines

    @property
    def OutputLines(self) -> list[EventLine]:
        return self._outputLines
 
    # @property
    # def _InputLine(self) -> EventLine | None:
    #     return self._inputLine
    
    # @property
    # def _OutputLine(self) -> EventLine | None:
    #     return self._outputLine
    
    # @_InputLine.setter
    # def InputLine(self, inputLine: EventLine | None) -> None: 
        
    #     #se rimuovo la linea di input, rimuovo tutti gli eventi che sto ascoltando  
    #     if self._inputLine is not None and inputLine is None:
    #         self._inputLine.removeAllObserverEvents(self)
   
    #     self._inputLine = inputLine
        
    # @_OutputLine.setter
    # def OutputLine(self, outputLine: EventLine | None) -> None:
    #     self._outputLine = outputLine

        
