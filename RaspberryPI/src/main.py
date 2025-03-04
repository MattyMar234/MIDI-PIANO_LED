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
import neopixel
from PianoElements.piano import Piano
from Midi.lineObserver import LineObserver
from Midi.eventLine import EventLine, EventData, EventType
from Midi.midiInterface import MidiInterface
from webServer import WebServer
import logging






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


def main() -> None:
    
    logging.info("Entering main loop. Press Control-C to exit.")
    
    #EVENT LINES
    midiEventsLine = EventLine()
    
    
    #-------DIPOSITIVI & CONNESSIONI-------#
    #piano
    piano = Piano(note_number=88, neoPixel_number=74, LED_strip_dataPin=board.D18)
    piano.InputLine = midiEventsLine
    piano.OutputLine = midiEventsLine
    piano.listenEvent(EventType.MIDI)
    piano.listenEvent(EventType.SETTING_CHANGE)
    
    #piano midi input
    pianoInterface = MidiInterface(MidiInterface.Mode.READ)
    pianoInterface.OutputLine = midiEventsLine
    piano.listenEvent(EventType.SETTING_CHANGE)

    #midi output  
    # pianoInterface = MidiInterface(MidiInterface.Mode.WRITE)
    # pianoInterface.InputLine = midiEventsLine
    # piano.listenEvent(EventType.MIDI)
    # piano.listenEvent(EventType.SETTING_CHANGE)

    #web server
    server = WebServer('0.0.0.0', 5000)
    server.OutputLine = midiEventsLine
    server.InputLine = midiEventsLine
    piano.listenEvent(EventType.MIDI)
    piano.listenEvent(EventType.SETTING_CHANGE)
    
    piano.start()
    server.start()
    
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
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()