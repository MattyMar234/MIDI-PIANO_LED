from enum import Enum, auto
import logging
import time
from typing import Optional
import rtmidi
import socket


from Midi.midiInterface import MidiInterface
from EventLine.eventLine import Event, EventData

class MidiInterfaceFactory():

    class MidiMode(Enum):
        READ = auto()
        WRITE = auto()

    class MidiInterfaceType(Enum):
        USB = auto()
        LAN = auto()

    class socketProtocol(Enum):
        UDP = auto()
        TCP = auto()

    @staticmethod
    def getAvailable_USB_Ports():
        midiin = rtmidi.MidiIn()
        available_ports = midiin.get_ports()
        return available_ports
    
    @staticmethod
    def create_interface(
        *,
        mode: MidiMode,
        connection_type: MidiInterfaceType,
        interface_name: Optional[str] = None,
        sendMidiDataEvent: Optional[Event] = None,
        reciveMidiDataEvent: Optional[Event] = None,
        
        usb_port_idx: int = None,
        ip_address: Optional[str] = None,
        udp_port: Optional[int] = None
      
    ) -> MidiInterface:
        
        interface = MidiInterface(interface_name, sendMidiDataEvent, reciveMidiDataEvent)

        if connection_type == MidiInterfaceFactory.MidiInterfaceType.USB and mode == MidiInterfaceFactory.MidiMode.READ:
            interface._setLoopFunctions(lambda self: MidiInterfaceFactory.__usb_read_function(self, usb_port_idx))

        elif connection_type == MidiInterfaceFactory.MidiInterfaceType.USB and mode == MidiInterfaceFactory.MidiMode.WRITE:
            interface._setLoopFunctions(lambda self: MidiInterfaceFactory.__usb_write_function(self, usb_port_idx))
            interface._setEventHandleFunction(lambda self, event: MidiInterfaceFactory.__handle_event_function(self, event))

        elif connection_type == MidiInterfaceFactory.MidiInterfaceType.LAN and mode == MidiInterfaceFactory.MidiMode.READ:
            interface._setLoopFunctions(lambda self: MidiInterfaceFactory.__lan_read_function(self, ip_address, udp_port))

        elif connection_type == MidiInterfaceFactory.MidiInterfaceType.LAN and mode == MidiInterfaceFactory.MidiMode.WRITE:
            interface._setLoopFunctions(lambda self: MidiInterfaceFactory.__lan_write_function(self, ip_address, udp_port))
            interface._setEventHandleFunction(lambda self, event: MidiInterfaceFactory.__handle_event_function(self, event))

        return interface
    
    @staticmethod
    def __usb_read_function(self: MidiInterface, port: int) -> None:
        #se non so che evento mandare aspetto un po
        print("heree")
        
        while self._sendMidiDataEvent is None or port is None:
            if self._port is None:
                logging.warning(f"Midi interface {self._worker_name} has no port set, waiting...")
                print(f"Midi interface {self._worker_name} has no port set, waiting...")
            if self._sendMidiDataEvent is None:
                logging.warning(f"Midi interface {self._worker_name} has no midiDataEvent set, waiting...")
                print(f"Midi interface {self._worker_name} has no midiDataEvent set, waiting...")
            time.sleep(0.800)
       
        logging.info(f"Midi interface {self._worker_name} connected to port {port}, starting read loop")
        print("heree")
        
        try:
            midiin = rtmidi.MidiIn()
            midiin.open_port(port)
            msg = None
            
            while self._running.is_set() and self._sendMidiDataEvent is not None:
                
                msg = midiin.get_message()
                
                if msg is not None:
                    while msg:
                        self.notifyEvent(EventData(msg, self._sendMidiDataEvent), as_thread=True)
                        msg = midiin.get_message()
                else:
                    time.sleep(0.002)
        finally:
            if midiin is not None:
                midiin.close_port()

    @staticmethod
    def __handle_event_function(self: MidiInterface, event: EventData) -> None:
        self._inputQueue.put(event.data)
                
    @staticmethod
    def __usb_write_function(self: MidiInterface, port: int) -> None:
        #se non so che evento mandare aspetto un po
        while self._sendMidiDataEvent is None or port is None:
            if port is None:
                logging.warning(f"Midi interface {self._worker_name} has no port set, waiting...")
            if self._sendMidiDataEvent is None:
                logging.warning(f"Midi interface {self._worker_name} has no midiDataEvent set, waiting...")
            time.sleep(0.800)

    
        try:
            midiout = rtmidi.MidiOut()
            midiout.open_port(self._port)
            msg = None
            
            while self._running.is_set() and self._reciveMidiDataEvent is not None:

                if not self._inputQueue.empty():
                    msg = self._inputQueue.get()
                else:
                    time.sleep(0.005)
                    continue

                while msg is not None:
                    midiout.send_message(msg) # assumendo che io non abbia modificato il messaggio
                    msg = self._inputQueue.get()
                
        finally:
            if midiout is not None:
                midiout.close_port()

    @staticmethod
    def __lan_read_function(self: MidiInterface, ip_address: str, udp_port: int) -> None:
        self._sock = None

        try:
            # --- Setup Socket UDP ---
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self._sock.bind((self.host, self.udp_port))
            self._sock.settimeout(0.1) # Timeout per non bloccare il loop
            logging.info(f"[MidiServer] In ascolto su {self.host}:{self.udp_port}")

            while self._running.is_set():
                try:
                    data, addr = self._sock.recvfrom(1024)
                    logging.debug(f"[MidiServer] Ricevuto {data} da {addr}")
                    self._midiout.send_message(data)
                except socket.timeout:
                    pass # Nessun dato in arrivo, continua
                except Exception as e:
                    logging.error(f"[MidiServer] Errore nella ricezione UDP: {e}")
        finally:
            if self._sock is not None:
                self._sock.close()
        

    def __lan_write_function(self: MidiInterface, ip_address: str, udp_port: int) -> None:
        
        self._sock = None

        try:
            # --- Setup Socket UDP ---
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self._sock.bind((self.host, self.udp_port))
            self._sock.settimeout(0.1) # Timeout per non bloccare il loop
            logging.info(f"[MidiServer] In ascolto su {self.host}:{self.udp_port}")

            while self._running.is_set():
                try:
                    if not self._inputQueue.empty():
                        msg = self._inputQueue.get()
                    else:
                        time.sleep(0.005)
                        continue

                    while msg is not None:
                        try:
                            midi_bytes = bytes(msg)
                            self._sock.sendto(midi_bytes, (self._broadcast_address, self.udp_port))
                            logging.debug(f"[MidiServer] Inviato in broadcast su {self.udp_port}")
                                    
                        except Exception as e:
                            logging.error(f"[MidiServer] Errore nell'invio UDP: {e}")
    
                        msg = self._inputQueue.get()

                except Exception as e:
                    logging.error(f"Error in LAN write function of {self._worker_name}: {e}")
        finally:
            if self._sock is not None:
                self._sock.close()
        


    