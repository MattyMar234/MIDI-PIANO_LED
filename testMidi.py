import time
import rtmidi
import random
import mido

# Crea un'istanza di MidiOut
# midi_out = rtmidi.MidiOut()

# # Abilita la porta virtuale
# midi_out.open_virtual_port("VirtualMIDIOut")

print("Porta MIDI virtuale 'VirtualMIDIOut' creata.")

# Funzione per inviare un messaggio MIDI (nota ON e OFF)
def send_midi_note(outport, note=60, velocity=36, duration=1):
    note_on = [0x90, note, velocity]  # Nota ON (Canale 1)
    note_off = [0x80, note, 0]        # Nota OFF (Canale 1)

    print(f"Inviando nota ON: {note_on}")
    #midi_out.send_message(note_on)
    outport.send(mido.Message('note_on', note=note, velocity=velocity))

    time.sleep(duration)

    print(f"Inviando nota OFF: {note_off}")
    outport.send(mido.Message('note_off', note=note, velocity=velocity))

# Invia una nota di test (Middle C)


# Mantieni il programma attivo per consentire ad altri software di vedere la porta
try:
    available_ports = mido.get_output_names()
    print("Porte MIDI disponibili:", available_ports)
    
    with mido.open_output("MyVirtualMIDI 1") as outport:
        while True:
            send_midi_note(outport, random.randrange(40, 70))
            time.sleep(1)
except KeyboardInterrupt:
    print("Chiusura della porta MIDI virtuale.")

