# import sys
# import threading
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
    
    print("Entering main loop. Press Control-C to exit.")
    
    
    midiLine = EventLine()
    
    
    #DIPOSITIVI
    piano = Piano(note_number=88, neoPixel_number=74, LED_strip_dataPin=board.D18)
    piano.InputLine = midiLine
    piano.OutputLine = midiLine
    piano.listenEvent(EventType.MIDI)
    
    pianoInterface = MidiInterface(MidiInterface.Mode.READ)
    pianoInterface.OutputLine = midiLine
        
    #midiLine.notify(None, EventData([123,234,234], EventType.MIDI))
    server = WebServer('0.0.0.0', 5000)
    server.OutputLine = midiLine
    
    piano.start()
    server.start()
    
    midiin = rtmidi.MidiIn()
    
    while True:
        
        
        while pianoInterface.isRunning():
            time.sleep(2)
            
        while not pianoInterface.isRunning():
    
            available_ports = midiin.get_ports()
            
            if available_ports:
                print("-"*80, end="\n\n")
                print("Dispositivi MIDI disponibili:")
                for i, port in enumerate(available_ports):
                    print(f"{i}: {port}")
                print("-"*80, end="\n\n")
                
                for i, port in enumerate(available_ports):
                    if "Digital Piano" in port:
                        print(f"Porta {i} selezionata: {port}")
                        pianoInterface.start(i)
                        #listen_port(midiin, i)
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
    main()