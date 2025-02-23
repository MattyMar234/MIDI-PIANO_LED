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
from Midi.midiLineObserver import MidiLineObserver, Mode, MidiEvent
from Midi.midiLine import MidiLine
from Midi.midiInterface import MidiInterface


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
    midiin = rtmidi.MidiIn()
    
    while True:
        
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
                    listen_port(midiin, i)
                    break
        
        time.sleep(2)
        

def main2() -> None:
    # leds = neopixel.NeoPixel(board.D18, 70, brightness=0.2)
    # leds.fill((0, 0, 0))
    
    midiLine = MidiLine()
    piano = Piano(note_number=88, neoPixel_number=74, LED_strip_dataPin=board.D18)
    pianoInterface = MidiInterface(mode=Mode.READ, midiLine=midiLine)
    
    midiLine.addObserver(piano)
    midiLine.addObserver(pianoInterface)
    
    midiin = rtmidi.MidiIn()
    available_ports = midiin.get_ports()
  
    pianoInterface.start(0)
    
    
    piano.start()
    time.sleep(4)
    piano.stop()
    

if __name__ == "__main__":
    main2()