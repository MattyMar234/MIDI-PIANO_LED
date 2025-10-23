
import asyncio
import logging
from EventLine.eventLine import EventData, EventLine, Event, LineObserver
import threading

class EventLineInterface(LineObserver):
    
    def __init__(self) -> None:
        # self._inputLine: EventLine | None = None
        # self._outputLine: EventLine | None = None
        
        self._inputLines: list[EventLine] = []
        self._outputLines: list[EventLine] = []
    
    def __del__(self) -> None:
        for line in self._outputLines:
            self._outputLines.remove(line)
            
        for line in self._inputLines:
            self._outputLines.remove(line)   
 
    def start_background_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    # --------------------------
    # GESTIONE LINEE
    # --------------------------

    def addInputLine(self, line: EventLine) -> None:
        """Aggiunge una linea di input"""
        if line not in self._inputLines:
            self._inputLines.append(line)
    
        
    def addOutputLine(self, line: EventLine) -> None:
        """Aggiunge una linea di output."""
        if line not in self._outputLines:
            self._outputLines.append(line)


    def removeInputLine(self, line: EventLine, direction: str = "input") -> None:
        """Rimuove una linea di input"""
        line.removeAllObserverEvents(self)
        self._inputLines.remove(line)


        
    def removeOutputLine(self, line: EventLine, direction: str = "input") -> None:
        """Rimuove una linea di output."""  
        
        if line in self._outputLines:
            self._outputLines.remove(line)
     

    # --------------------------
    # FUNZIONI EVENTI
    # --------------------------
    
    def listenEvent(self, event: Event,  line: EventLine) -> True:
        """Registra l'interfaccia come observer di un certo evento su tutte le linee di input."""
       
        assert isinstance(event, Event), f"Il parametro event deve essere di tipo Event. Passato: {type(event)}"
        assert isinstance(line, EventLine), f"Il parametro line deve essere di tipo EventLine. Passato: {type(event)}"
       
        for line in self._inputLines:
            if event in line.getAvailableEvents():
                line.addObserver(self, event)
                logging.info(f"{self} ora ascolta l'evento {event} sulla linea {line}")
                return True
        
        logging.warning(f"Nessuna linea di input disponibile per l'evento {event}")
        return False
        
    def ignoreEvent(self, event: Event, line: EventLine) -> None:
        """Rimuove l'interfaccia come observer di un certo evento su tutte le linee di input."""
        
        assert type(event) is type(Event), "Il parametro event deve essere di tipo Event"
        assert type(line) is type(EventLine), "Il parametro line deve essere di tipo EventLine"
       
        
        for line in self._inputLines:
            if event in line.getAvailableEvents():
                line.removeObserver(self, event)
    
    def notifyEvent(self, event: EventData, as_thread: bool = True, async_mode: bool = False) -> bool:
        """Invia un evento a tutte le linee di output"""
        
        if not self._outputLines:
            logging.error("Nessuna linea di output impostata")
            return False
        
        
        for line in self._outputLines:
            if not as_thread and not async_mode:
                line.notify(self, event)
                
            elif not as_thread and async_mode:
                asyncio.run(line.async_notify(self, event))
            
            elif as_thread and not async_mode:
                threading.Thread(target=lambda: line.notify(self, event), daemon=True).start()
                
            else:
                threading.Thread(target=lambda: asyncio.run(line.async_notify(self, event)), daemon=True).start()

        
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

        
