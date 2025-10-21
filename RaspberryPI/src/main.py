# import sys
# import threading
import globalData
import rtmidi
# print(rtmidi.__file__)
# from rtmidi.midiutil import open_midiport
# from rtmidi.midiutil import open_midiinput

# import mido
import time
import board
import digitalio
import neopixel
import argparse
import logging
import asyncio

#from webServer import WebServer
from Midi.midiInterface import MidiInterface
from EventLine.eventLine import EventFactory, Event, EventData, EventLine
from PianoElements.piano import PianoLED





def print_data(data) -> None:
    temp = ", ".join("0x{:02x}".format(num) for num in data)
    temp = f"Data: [{temp}]"
    print(temp)

def listen_port(midiin, port) -> None:
    print(f"Listening on port {port}")
    
    try:
        midiin.open_port(port)
        while True:
            msg = midiin.get_message()
            if msg:
                data, dt = msg[0], msg[1]
                print_data(data=data)
            else:
                time.sleep(0.01)
    except Exception as e:
        print(e)


async def main() -> None:
    
    logging.info("Entering main loop. Press Control-C to exit.")
    logging.info("")
    logging.info("-"*80)
    
    
    #EVENT LINES
    NotePressedEvent = EventFactory.createEventType("NOTE_PRESSED")
    NoteReleasedEvent = EventFactory.createEventType("NOTE_RELEASED")
    MidiDataEvent = EventFactory.createEventType("MIDI")
    SettingChangeEvent = EventFactory.createEventType("SETTING_CHANGE")
    
    ColorChangeEvent = EventFactory.createEventType("COLOR_CHANGE")
    changeEffectEvent = EventFactory.createEventType("CHANGE_EFFECT")
    
    logging.info("-"*80)
    
    midiEventsLine = EventLine()
    midiEventsLine.registerEvent(NotePressedEvent)
    midiEventsLine.registerEvent(NoteReleasedEvent)
    midiEventsLine.registerEvent(MidiDataEvent)
    midiEventsLine.registerEvent(SettingChangeEvent)
    
    settingsLine = EventLine()
    settingsLine.registerEvent(ColorChangeEvent)
    settingsLine.registerEvent(changeEffectEvent)
    
    logging.info("-"*80)
    
    #-------DIPOSITIVI & CONNESSIONI-------#
    #piano
    piano = PianoLED(note_number=88, neoPixel_number=74, LED_strip_dataPin=board.D18)
    piano.addInputLine(midiEventsLine)
    piano.addOutputLine(midiEventsLine)
  
    piano.listenEvent(event = MidiDataEvent, line=midiEventsLine)
    piano.listenEvent(event = SettingChangeEvent, line=midiEventsLine)
    piano.setMidiDataEvent(MidiDataEvent)
    piano.start()
    
    #piano midi input
    pianoInterface = MidiInterface(MidiInterface.Mode.READ, "PianoMIDI", 0, MidiDataEvent)
    pianoInterface.addOutputLine(midiEventsLine)
    


    #midi output  
    # pianoInterface = MidiInterface(MidiInterface.Mode.WRITE)
    # pianoInterface.InputLine = midiEventsLine
    # piano.listenEvent(EventType.MIDI)
    # piano.listenEvent(EventType.SETTING_CHANGE)

    # #web server
    # server = WebServer('0.0.0.0', 5000)
    # server.OutputLine = midiEventsLine
    # server.InputLine = midiEventsLine
    # piano.listenEvent(Event.MIDI)
    # piano.listenEvent(Event.SETTING_CHANGE)
    
    
    # server.start()
    
    midiin = rtmidi.MidiIn()
    available_ports: int = -1
    
    while True:    

        #ogni tanto controllo se l'interfaccia è attiva
        while pianoInterface.isRunning():
            time.sleep(2)
            available_ports = -1
            
        #cerca la porta midi da utilizzare    
        while not pianoInterface.isRunning():
    
            ports = midiin.get_ports()
            number = len(ports)

            #verifico se ci sono nuove porte
            if number != available_ports:
                available_ports = number

                if number == 0:
                    logging.info("No Midi Port found")
                else:
                    logging.info("-"*80)
                    logging.info("Avaialble MIDI device:")
                
                    for i, port in enumerate(ports):
                        logging.info(f"- {i}: {port}")
                    logging.info("-"*80)
                
                for i, port in enumerate(ports):
                    if globalData.PIANO_PORT_NAME in port:
                        #print(f"Porta {i} selezionata: {port}")
                        pianoInterface.start(i)
                        break
            
            time.sleep(2)
        

def main2() -> None:
    pass
    # leds = neopixel.NeoPixel(board.D18, 70, brightness=0.2)
    # leds.fill((0, 0, 0))
    
    # midiLine = EventLine()
    # piano = Piano(note_number=88, neoPixel_number=74, LED_strip_dataPin=board.D18)
    # pianoInterface = MidiInterface(mode=Mode.READ, midiLine=midiLine)
    
    # midiLine.addObserver(piano)
    # midiLine.addObserver(pianoInterface)
    
    # midiin = rtmidi.MidiIn()
    # available_ports = midiin.get_ports()
  
    # pianoInterface.start(0)
    
    
    # piano.start()
    # time.sleep(4)
    # piano.stop()
    
def test() -> None:
    """
    Funzione di test per far lampeggiare un GPIO a 2 Hz.
    """
    
    GPIOs = [board.D18]
    leds = []
    
    logging.info(f"Avvio del test di lampeggio sui GPIO {GPIOs} a 2 Hz. Premere Ctrl+C per uscire.")
    
    
    # Configura il pin come output digitale
    for LED_PIN in GPIOs:
        try:
            led = digitalio.DigitalInOut(LED_PIN)
            led.direction = digitalio.Direction.OUTPUT
            leds.append(led)     
        except Exception as e:
            logging.error(f"Impossibile inizializzare il pin GPIO {LED_PIN}. Errore: {e}")
            
    if leds == []:
        logging.error("Nessun GPIO valido trovato. Uscita dal test.")
        return
    
    # 2 Hz = 2 cicli al secondo = 1 ciclo ogni 0.5 secondi
    # 0.25s acceso, 0.25s spento
    period = 0.5
    on_time = period / 2
    
    try:
        while True:  
            for led in leds:
                led.value = True
            
            time.sleep(on_time)
            
            for led in leds:
                led.value = False
            
            time.sleep(on_time)
            
    except KeyboardInterrupt:
        logging.info("Test interrotto dall'utente.")
    finally:
        # Assicuriamoci che il pin sia spento all'uscita
        logging.info(f"Spegnimento del pin...")
        for led in leds:
            led.value = False
            led.deinit()
        
        


if __name__ == "__main__":

    # Creazione del parser per gli argomenti da riga di comando
    parser = argparse.ArgumentParser(description="Controller LED per Piano con interfaccia MIDI e Web.")
    
    functions = {
        "main": lambda: asyncio.run(main()),
        "test": test
    }

    # Argomento per selezionare la funzione da eseguire
    parser.add_argument(
        '--function', 
        type=str, 
        choices=['main', 'test'], 
        default='main',
        help="Seleziona la funzione da avviare: 'main' (default) per l'applicazione completa, 'test' per il test dei GPIO."
    )

    # Argomento per selezionare il livello di logging
    parser.add_argument(
        '--log-level', 
        type=str, 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 
        default='INFO',
        help="Imposta il livello di logging (default: INFO)."
    )

    # Esegui il parsing degli argomenti
    args = parser.parse_args()

    # Configura il logging in base all'argomento fornito
    # Usiamo getattr per convertire la stringa in una costante del modulo logging
    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    logging.info(f"Funzione selezionata: {args.function}")
    logging.info(f"Livello di logging impostato a: {args.log_level.upper()}")

    # Avvia la funzione corretta in base all'argomento
    # if args.function == 'main':
    #     try:
    #         asyncio.run(main())
    #     except KeyboardInterrupt:
    #         logging.info("Programma principale interrotto.")
    # elif args.function == 'test':
    #     test()
    
    functions[args.function]()

