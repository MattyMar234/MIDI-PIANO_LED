#ifndef GLOBAL_
#define GLOBAL_


#define DEBUG_PORT Serial
#define BlueTooth Serial2


//Led stript
#define PIN_PIXELS     6
#define BLUETOOTH_INTERRUPT_PIN 18
#define BUTTON1_INTERRUPT_PIN 19
#define BUTTON2_INTERRUPT_PIN 2
#define BUTTON3_INTERRUPT_PIN 3

//paramLed stript



//#define DisableDisplay
//#define CommandsOutput
//define Debug1
//define DebugColor
#define NoteOffset 21
#define NotePerOttava 12
#define PianoTotalNote 88

#define PianoLastNote 88
#define PianoFistNote 0
#define TotalMenuAvailable  4

#define RotaryDirection 3
#define RotaryClockforUpdate 5

#define MAX_dissolvenceDuration 2000
#define MIN_dissolvenceDuration 20

#define MAXTranspose +12
#define MINTranspose -12

#define MAX_Brightness 200
#define MIN_Brightness 0

#define MAX3421E_InterruptPin 2
#define SERIAL_BUFFER_SIZE 32

//================== MIDI command ==================//
#define Command_NoteOff         0x80
#define Command_NoteOn          0x90
#define Command_Aftertouch      0xA0
#define Command_Controller      0xB0
#define Command_PatchChange     0xC0
#define Command_ChannelPressure 0xD0
#define Command_PitchBend       0xE0
#define Command_contrtols       0xF0

#define Command_contrtols1   0xF0	//start of system exclusive message	variable
#define Command_contrtols2   0xF1	//MIDI Time Code Quarter Frame (Sys Common)	
#define Command_contrtols3   0xF2	//Song Position Pointer (Sys Common)	
#define Command_contrtols4   0xF3	//Song Select (Sys Common)	
#define Command_contrtols5   0xF4	//???	
#define Command_contrtols6   0xF5	//???	
#define Command_contrtols7   0xF6	//Tune Request (Sys Common)	
#define Command_contrtols8   0xF7	//end of system exclusive message	0
#define Command_contrtols9   0xF8	//Timing Clock (Sys Realtime)	
#define Command_contrtols10  0xFA	//Start (Sys Realtime)	
#define Command_contrtols11  0xFB	//Continue (Sys Realtime)	
#define Command_contrtols12  0xFC	//Stop (Sys Realtime)	
#define Command_contrtols13  0xFD	//???	
#define Command_contrtols14  0xFE	//Active Sensing (Sys Realtime)	
#define Command_contrtols15  0xFF	//System Reset (Sys Realtime)

#define ColorAvailable 48
#define LuminositaIncremento 10
#define MaxNoteNumber 108
#define MinNoteNumber 21
#define MaxVelocity 150
#define velocityLevel 86


/*================================ PROTOTIPI ================================*/
float NoteToLed_Conversion(uint8_t note);
void ChangeColor(uint8_t value);
void LoadColorFromFlash();
void MenuOpzioni();
void ButtonHandler(uint8_t number);
void PrintMenu(uint8_t n1, uint8_t n2, uint8_t n3);

//operazioni sui led
void LedState(uint8_t note, uint8_t led);
void changeBrightness(int8_t value);
uint8_t VelocityToColor(uint8_t v);
void randomColor();

//MIDI
inline void MIDI_Poll();
void MIDI_NotePressed(uint8_t NoteNumber, uint8_t velocity);
void MIDI_NoteRelased(uint8_t NoteNumber);
void synchronize();
void handle_Midi_status(uint8_t data);
void dumpData(uint8_t* buf);

inline void Serial_Command(register uint8_t data);


#endif
