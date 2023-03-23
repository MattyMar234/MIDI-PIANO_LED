#ifndef SYSTEM_H
#define SYSTEM_H

#include <Arduino.h>


class SystemControls 
{
    public:
        static boolean Enable_USB_SerialDebug;
        static boolean Enable_MIDI_COMMAND_SerialDebug;
        static boolean Enable_MIDI_NOTE_SerialDebug;
        static boolean Enable_MIDI_SYSTEM_SerialDebug;
        static boolean USB_Device_Available; 
        static boolean USB_POLLING_FLAG; 
        //static boolean USB_STATE_ISCHANGED;
        static uint8_t USB_STATE;
        static boolean USB_REFRESH_FLAG; 
        static boolean USB_UPDATE_FLAG; 
};

boolean SystemControls::Enable_MIDI_COMMAND_SerialDebug = false;
boolean SystemControls::Enable_MIDI_SYSTEM_SerialDebug = false;
boolean SystemControls::Enable_MIDI_NOTE_SerialDebug = false;
boolean SystemControls::Enable_USB_SerialDebug = false;
boolean SystemControls::USB_Device_Available = false;
//boolean SystemControls::USB_STATE_ISCHANGED = false;
boolean SystemControls::USB_POLLING_FLAG = false;
boolean SystemControls::USB_REFRESH_FLAG = false;
boolean SystemControls::USB_UPDATE_FLAG = false;
uint8_t SystemControls::USB_STATE = 0;


#endif // SYSTEM_H