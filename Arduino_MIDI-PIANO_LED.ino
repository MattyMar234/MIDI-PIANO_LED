#include <usbhub.h>    
#include "usbh_midi.h"

#include "Piano.h"
#include "HardwareTimer.h"
#include "SystemControls.h"
#include "BlueTooth.h"

#include <SoftwareSerial.h>

volatile uint8_t LED_Update_Index = (int)TOTAL_LED - 1;
volatile uint8_t PerscalerCounter = 0;


ISR(TIMER1_COMPA_vect);

Piano MidiPiano(PIN_PIXELS);
USB Usb;
USBH_MIDI  Midi(&Usb);



Bluetooth<HardWareSerial1> BlueTooth = Bluetooth<HardWareSerial1>();
ArrayList<uint8_t, 40> SerialBuffer = ArrayList<uint8_t, 40>();

ISR(TIMER1_COMPA_vect) 
{
  if(!SystemControls::USB_UPDATE_FLAG) {
    PerscalerCounter = ++PerscalerCounter % 10;
    LED_Update_Index = ++LED_Update_Index % (int)TOTAL_LED; //[0,74]

    SystemControls::USB_UPDATE_FLAG = true; 

    if(LED_Update_Index == 0) {
      SystemControls::USB_REFRESH_FLAG = true; 
    }
  }
  
  //375HZ
  if(PerscalerCounter == 0) {
    SystemControls::USB_POLLING_FLAG = true; 
  }
}

void BlueTooth__Interrupt__RX() {
  SerialBuffer.push(BlueTooth.read());
}


void setup() 
{
  SystemControls::Enable_USB_SerialDebug = true;
  SystemControls::Enable_MIDI_NOTE_SerialDebug = true;

  Serial.begin(115200);

  BlueTooth.begin(9600);
  BlueTooth.attachInterrupt_RX(BlueTooth__Interrupt__RX);

  MidiPiano.Print();

  /*==================== INIZIALIZZAZIONE USB-HOST ====================*/
  bool HostStatus = false;
  
  do {
    //if(Controls.SerialDebug) 
    DEBUG_PORT.print(F("Init USB Host: "));
    
    if (Usb.Init() == -1) {
      //if(Controls.SerialDebug) 
      DEBUG_PORT.println(F("Errore"));
      delay(2000);
    } 
    else {
      HostStatus = true;
      //if(Controls.SerialDebug) 
      DEBUG_PORT.println(F("Done"));
    }
  } while(!HostStatus);

  /*==================== INIZIALIZZAZIONE TIMER ====================*/
  Hardware_TimerCounter1::setAsTimer(LED_REFRESH_RATE*TOTAL_LED, INTERRUPT_ON_COMPA); //4.5KHz
}



void loop() 
{
  register uint16_t USB_State;
  
  // ==================== [<LED>] ==================== //
  if(SystemControls::USB_UPDATE_FLAG) {
    SystemControls::USB_UPDATE_FLAG = false;
    MidiPiano.UpDateLED(LED_Update_Index);
  }
  
  if(SystemControls::USB_REFRESH_FLAG) {
    SystemControls::USB_REFRESH_FLAG = false; 
    MidiPiano.refresh();
  }

  // ==================== [Serial Data] ==================== //
  if(SerialBuffer.lenght() != 0) {
    Serial_Command(SerialBuffer.front());
  }
  else if(Serial.available()) {
    Serial_Command(Serial.read());
  }
  
  // ==================== [<USB>] ==================== //
  if(SystemControls::USB_POLLING_FLAG) { //SystemControls::USB_POLLING_FLAG
    SystemControls::USB_POLLING_FLAG = false;
    
    /* ==================== [USB POOLING] ==================== */
    Usb.Task();
    USB_State = Usb.getUsbTaskState();
    
    /* ==================== [USB STATE] ==================== */
    if(SystemControls::USB_STATE != USB_State) {//
      SystemControls::USB_STATE = USB_State;

      if(SystemControls::Enable_USB_SerialDebug)
        DEBUG_PORT.print(F("USB port state: "));

      if(USB_State == USB_STATE_DETACHED)      {
        DEBUG_PORT.println(F("USB_STATE_DETACHED\n")); 
        
      }else if(USB_State == USB_DETACHED_SUBSTATE_INITIALIZE) {
        if(SystemControls::Enable_USB_SerialDebug)
          DEBUG_PORT.println(F("USB_DETACHED_SUBSTATE_INITIALIZE"));   
        
      }else if(USB_State == USB_DETACHED_SUBSTATE_ILLEGAL) {
        if(SystemControls::Enable_USB_SerialDebug)
          DEBUG_PORT.println(F("USB_DETACHED_SUBSTATE_ILLEGAL"));  
                             
      }else if(USB_State == USB_ATTACHED_SUBSTATE_SETTLE) {
        if(SystemControls::Enable_USB_SerialDebug)
         DEBUG_PORT.println(F("USB_ATTACHED_SUBSTATE_SETTLE"));  
         
      }else if(USB_State == USB_ATTACHED_SUBSTATE_RESET_DEVICE) {
        if(SystemControls::Enable_USB_SerialDebug)
          DEBUG_PORT.println(F("USB_ATTACHED_SUBSTATE_RESET_DEVICE")); 
        
      }else if(USB_State == USB_DETACHED_SUBSTATE_WAIT_FOR_DEVICE) {
        if(SystemControls::Enable_USB_SerialDebug)
          DEBUG_PORT.println(F("USB_DETACHED_SUBSTATE_WAIT_FOR_DEVICE"));
        
      }else if(USB_State == USB_ATTACHED_SUBSTATE_WAIT_RESET_COMPLETE) {
        if(SystemControls::Enable_USB_SerialDebug)
          DEBUG_PORT.println(F("USB_ATTACHED_SUBSTATE_WAIT_RESET_COMPLETE"));
        
      }else if(USB_State == USB_ATTACHED_SUBSTATE_WAIT_SOF) {
        if(SystemControls::Enable_USB_SerialDebug)
          DEBUG_PORT.println(F("USB_ATTACHED_SUBSTATE_WAIT_SOF"));
        
      }else if(USB_State == USB_ATTACHED_SUBSTATE_WAIT_RESET) {
        if(SystemControls::Enable_USB_SerialDebug)
          DEBUG_PORT.println(F("USB_ATTACHED_SUBSTATE_WAIT_RESET"));
        
      }else if(USB_State == USB_ATTACHED_SUBSTATE_GET_DEVICE_DESCRIPTOR_SIZE) {
        if(SystemControls::Enable_USB_SerialDebug)
          DEBUG_PORT.println(F("USB_ATTACHED_SUBSTATE_GET_DEVICE_DESCRIPTOR_SIZE"));
        
      }else if(USB_State == USB_STATE_CONFIGURING) {
        if(SystemControls::Enable_USB_SerialDebug)
          DEBUG_PORT.println(F("USB_STATE_CONFIGURING"));
        
      }else if(USB_State == USB_STATE_ERROR) {
        if(SystemControls::Enable_USB_SerialDebug)
          DEBUG_PORT.println(F("USB_STATE_ERROR"));  
        
      }else if(USB_State == USB_STATE_RUNNING) {
        if(SystemControls::Enable_USB_SerialDebug) {
          DEBUG_PORT.println(F("USB_STATE_RUNNING"));
          DEBUG_PORT.println(F("[MIDI] SEND SYSTEM RESET..."));
        }
        
          static uint8_t sysexmsg[] = {0xF0, 0x7F, 0x7F, 0x02, 0x7F, 0x0A, 0xF7};
          static uint8_t sizeofsysex = 7;

          Midi.SendSysEx(sysexmsg, sizeofsysex);
          //uint8_t sysexmsg[1] = {0xFF};
          /*Serial.write(0xF0);
          Serial.write(0x7F);
          Serial.write(0x7F); //device id 7F = 127 all channels
          Serial.write(0x02);
          Serial.write(0x7F); // command format 7F = all devices
          Serial.write(0x0A); // action 0x0A= reset
          Serial.write(0xF7);*/

      }else {
         if(SystemControls::Enable_USB_SerialDebug)
          DEBUG_PORT.println(F("UNKNOW STATE\n"));
      }
    }

    /* ==================== [MIDI reading] ==================== */
    if(SystemControls::USB_STATE == USB_STATE_RUNNING && Midi) {
        MIDI_Poll(); 
    }
  }
}

inline void Serial_Command(register uint8_t data) {
    static char buffer[SERIAL_BUFFER_SIZE];
    static uint8_t bufferIndex = 0;

    //se diverso dal comado di conferma, accodo i dati
    if(data >= 32 && data <= 126) {
     if(bufferIndex < SERIAL_BUFFER_SIZE) {
        buffer[bufferIndex++] = (char)data;
      }
    }
    else if(data == '\n' || data == '\r') {
      String str;

      for(uint8_t i = 0; i < bufferIndex; i++) {
        str += buffer[i];
      }

      if(str == F("/nextColor")) {
        if(SystemControls::Enable_USB_SerialDebug)
          DEBUG_PORT.println(F("Ok incrementColor"));
        MidiPiano.nextColor();
      }
      else if(str == F("/previusColor")) {
        if(SystemControls::Enable_USB_SerialDebug)
          DEBUG_PORT.println(F("Ok decrementColor"));
        MidiPiano.previousColor();
      }
      else if(str == F("/changing_RGBcolor")) {
        MidiPiano.RGB_Color();
      }
      else if(str == F("/resetTranspose")) {
        MidiPiano.ResetTranspose();
      }
      else if(str == F("/incrementTranspose")) {
        MidiPiano.IncrementTranspose();
      }
      else if(str == F("/decrementTranspose")) {
        MidiPiano.DecrementTranspose();
      }
      else if(str == F("/noneEffect")) {
        MidiPiano.setEffect(NONE_EFFECT);
      }
      else if(str == F("/noDelayEffect")) {
        MidiPiano.setEffect(NO_DELAY_EFFECT);
      }
      else if(str == F("/dissolvenzeEffect")) {
        MidiPiano.setEffect(NORMAL_EFFECT);
      }
      else if(str == F("/randomOnForceEffect")) {
        MidiPiano.setEffect(RANDOM_ON_FORCE_EFFECT);
      }
      bufferIndex = 0;
    }
    
}


inline void MIDI_Poll()
{
  static uint8_t buffer[3];
  register uint8_t Command;
  register uint8_t channel;

  if (Midi.RecvData(buffer) == 0) 
    return;

  Command = buffer[0] & 0xF0;
  channel = buffer[0] & 0x0F;

  switch (Command)
  {
    case Command_NoteOff: {
      if(SystemControls::Enable_MIDI_NOTE_SerialDebug) DEBUG_PORT.println(F("NoteOff"));
      MidiPiano.RelaseNote(buffer[1]);
    break;
    }

    case Command_NoteOn: {
      if(buffer[2] == 0) {
        if(SystemControls::Enable_MIDI_NOTE_SerialDebug) {
          DEBUG_PORT.print(F("Note Relased: ")); Serial.println(buffer[1]);
        }
      MidiPiano.RelaseNote(buffer[1]);
      } 
      else {
        if(SystemControls::Enable_MIDI_NOTE_SerialDebug) {
          DEBUG_PORT.print(F("Note Pressed: ")); Serial.print(buffer[1]);
          DEBUG_PORT.print(F(" | Velocity: "));  Serial.println(buffer[2]);
        }
        MidiPiano.PressNote(buffer[1], buffer[2]);
      }
      break;
    }

    case Command_Aftertouch: {
      if(SystemControls::Enable_MIDI_COMMAND_SerialDebug){
        DEBUG_PORT.println(F("Aftertouch"));
      }
      break;

    }
    case Command_Controller: {
      if(SystemControls::Enable_MIDI_COMMAND_SerialDebug){
        DEBUG_PORT.println(F("Controller"));
      }
      break;
    }
    case Command_PatchChange: {
      if(SystemControls::Enable_MIDI_COMMAND_SerialDebug){
        DEBUG_PORT.println(F("PatchChange"));
      }
      break;
    }

    case Command_PitchBend: {
      if(SystemControls::Enable_MIDI_COMMAND_SerialDebug){
        DEBUG_PORT.println(F("PitchBend"));
      }
      break;
    }

    case Command_contrtols: {
      switch (buffer[0]) 
      {
        case 0xF8:
          if(SystemControls::Enable_MIDI_SYSTEM_SerialDebug) {
            DEBUG_PORT.println(F("contrtols/Status => Timing Clock"));
          }
        break;
    

        case 0xFE:
          if(SystemControls::Enable_MIDI_SYSTEM_SerialDebug) {
            DEBUG_PORT.println(F("contrtols/Status => Active Sensing"));
          }
        break;

      }
      break;
    }

    default: {
      if(SystemControls::Enable_MIDI_SYSTEM_SerialDebug){
        DEBUG_PORT.println(F("Comando Sconosciuto"));
      }
      break;
    }
  }
}
