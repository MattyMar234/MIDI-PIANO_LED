#ifndef PIANO_H
#define PIANO_H

#include <Arduino.h>
#include "global.h" 
#include "ArrayList.h"
#include "ArrayList.cpp"
#include "WS2812_Interface.h"
#include "Global.h"


#define NoteFast 127

#define TOTAL_NOTE 88
#define PIANO_TOTAL_WHITE_NOTE 52
#define PIANO_NOTE_LENGHT 2.4
#define LED_LENGHT  1.65

#define NOTE_START_OFFSET 21
#define NOTE_END_WITH_OFFSET (NOTE_START_OFFSET + TOTAL_NOTE - 1)

#define PIANO_LENGHT (PIANO_TOTAL_WHITE_NOTE*PIANO_NOTE_LENGHT)
#define TOTAL_LED (PIANO_LENGHT/LED_LENGHT)

#define offset1 PIANO_NOTE_LENGHT*7
#define offset2 PIANO_NOTE_LENGHT*5

#define LED_REFRESH_RATE 60 //60Hz
#define LED_STATE_FLAG 0x01

//LED EFFECT
#define NONE_EFFECT 0
#define NO_DELAY_EFFECT 1
#define NORMAL_EFFECT 2
#define RGB_EFFECT 2

//formattazione
#define ADDESS_DIGIT_SIZE 4


const uint8_t Colors [ColorAvailable][3] PROGMEM =  {
    
//   R   G    B
    255, 0  , 0  ,
    255, 32 , 0  ,
    255, 64 , 0  ,
    255, 96 , 0  ,
    255, 128, 0  ,
    255, 160, 0  ,
    255, 192, 0  ,
    255, 224, 0  , 
    255, 255, 0  ,
    224, 255, 0  ,
    192, 255, 0  ,
    160, 255, 0  ,
    128, 255, 0  ,
    96 , 255, 0  ,
    64 , 255, 0  ,
    32 , 255, 0  ,  //15
    0  , 255, 0  ,
    0  , 255, 32 ,
    0  , 255, 64 ,
    0  , 255, 96 ,
    0  , 255, 128,  //20
    0  , 255, 160,
    0  , 255, 192,
    0  , 255, 224,
    0  , 255, 255,
    0  , 224, 255,
    0  , 192, 255,  //26
    0  , 160, 255,
    0  , 128, 255,
    0  , 96 , 255,
    0  , 64 , 255, //30
    0  , 32 , 255,
    0  , 0  , 255,
    32 , 0  , 255,
    64 , 0  , 255,
    96 , 0  , 255,
    128, 0  , 255, //36
    160, 0  , 255,
    192, 0  , 255,
    224, 0  , 255,
    255, 0  , 255,//40
    255, 0  , 224,
    255, 0  , 192,
    255, 0  , 160,
    255, 0  , 128, //44
    255, 0  , 96,
    255, 0  , 64,
    255, 0  , 32
};


typedef struct Nota
{
    //private:

    //public:
        uint8_t NotaNumber;
        bool Pressed;
        uint8_t Velocity; //MAX 127
        uint8_t LED_Index;

}Nota;

class LED
{
    private:
        inline uint8_t GetNote_Number() {
            return ((this->LedFlags >> 1) & 0x03);
        }

    public:
        //ArrayList<Nota*> attachedNote;

        //puntatore alla prima nota
        Nota* FistNotePointer = NULL;

        //luminosita attuale
        uint8_t actualBrightness = 0x00;

        //tempo per la dissolvenza (delay/riduzione luminosità)
        unsigned int DissolvenceTime = 0x00;     
        
        uint8_t LedFlags = 0x00;                 
        //b0 stato LED (ON/OFF), 
        //b1 numero note bit 1 
        //b2 numero note bit 2 
            
        LED();
        void addNote(Nota *p);
        void PrintAddress();
        void Update();
        bool check_turnOn();
        
        
};




class Piano
{
    private:

        WS2812_interface *LED_Interface;
        uint8_t LED_MAX_Brightness = 200;
        uint8_t Trasnspose = 0;//+-127
        uint8_t Piano_LED_Animation = NORMAL_EFFECT;
        

        Nota PianoNote[TOTAL_NOTE];
        LED  PianoLED[(int)TOTAL_LED];
   
        //da sistemare
        bool AlteredArray[NotePerOttava] = {false, true, false, true, false, false, true, false, true, false, true, false};
        uint8_t ToWhiteNote[NotePerOttava] = {0,0,1,1,2,3,3,4,4,5,5,6};

 

        inline boolean isOn(register uint8_t LED_index) {
            return ((PianoLED[LED_index].LedFlags & LED_STATE_FLAG) == 0x01);
        }

        inline boolean isOff(register uint8_t LED_index) {
            return ((PianoLED[LED_index].LedFlags & LED_STATE_FLAG) == 0x00);
        }

        inline void turnOn(register uint8_t LED_index, uint8_t register r, uint8_t register g, uint8_t register b) {
            LED_Interface->SetLedColor(LED_index, r, g, b);
            PianoLED[LED_index].LedFlags |= 0x01;
        }

        inline void turnOff(register uint8_t LED_index) {
            LED_Interface->SetLedColor(LED_index, 0x00, 0x00, 0x00);
            PianoLED[LED_index].LedFlags &= 0xFE;
        }

        float NoteToLed_Conversion(uint8_t note);

    public:

        Piano(uint8_t pin);
        void PressNote(uint8_t note, uint8_t velocity);
        void RelaseNote(uint8_t note);
        void UpdateNote(uint8_t note);
        void PrintInformation(Nota *p);
        void UpDateLED(const register uint8_t LED_index);
        void refresh();
        void Print();
};

//Note Piano::PianoNote[TOTAL_NOTE]



#endif // PIANO_H