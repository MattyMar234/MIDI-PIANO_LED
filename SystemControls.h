#ifndef SYSTEM_H
#define SYSTEM_H

#include <Arduino.h>


class SystemControls 
{
    public:
        static volatile boolean Enable_USB_SerialDebug;
        static volatile boolean Enable_MIDI_COMMAND_SerialDebug;
        static volatile boolean Enable_MIDI_NOTE_SerialDebug;
        static volatile boolean Enable_MIDI_SYSTEM_SerialDebug;
        static volatile boolean USB_Device_Available; 
        static volatile boolean USB_POLLING_FLAG; 
        //static boolean USB_STATE_ISCHANGED;
        static volatile uint8_t USB_STATE;
        static volatile boolean USB_REFRESH_FLAG; 
        static volatile boolean USB_UPDATE_FLAG; 

        static volatile boolean BT_CONNECTED_MESSAGE;
        static volatile boolean BT_CONNECTION_STATE;
};

volatile boolean SystemControls::Enable_MIDI_COMMAND_SerialDebug = false;
volatile boolean SystemControls::Enable_MIDI_SYSTEM_SerialDebug = false;
volatile boolean SystemControls::Enable_MIDI_NOTE_SerialDebug = false;
volatile boolean SystemControls::Enable_USB_SerialDebug = false;
volatile boolean SystemControls::USB_Device_Available = false;
//boolean SystemControls::USB_STATE_ISCHANGED = false;
volatile boolean SystemControls::USB_POLLING_FLAG = false;
volatile boolean SystemControls::USB_REFRESH_FLAG = false;
volatile boolean SystemControls::USB_UPDATE_FLAG = false;
volatile uint8_t SystemControls::USB_STATE = 0;

volatile boolean SystemControls::BT_CONNECTED_MESSAGE = false;
volatile boolean SystemControls::BT_CONNECTION_STATE = false;


#endif // SYSTEM_H