#ifndef PIANO_H
#define PIANO_H

#include <Arduino.h>
#include "global.h" 
#include "ArrayList.h"
#include "ArrayList.cpp"
#include "WS2812_Interface.h"
#include "Global.h"


//Parametri MIDI
#define NoteFast 127

//parametri PianoForte
#define TOTAL_NOTE 88
#define PIANO_TOTAL_WHITE_NOTE 52
#define PIANO_TOTAL_BLACK_NOTE 36
#define NOTE_START_OFFSET 21
#define WHITE_NOTE_PER_OCTAVE 7
#define LED_STRIP_START_OFFSET 0

#define PIANO_NOTE_LENGHT 2.4
#define PIANO_WHITE_NOTE_LENGHT 2.4
#define PIANO_BLACK_NOTE_LENGHT 1.2
#define BLACK_NOTE_OFFSET_FROM_WHITE_NOTE ((PIANO_WHITE_NOTE_LENGHT/3)*2)
#define LED_LENGHT  1.65

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
#define RANDOM_ON_FORCE_EFFECT 3

#define STATIC_COLOR 0
#define DYNAMIC_RGB_COLOR 1
#define COLOR_AVAILABLE 48

//formattazione
#define ADDESS_DIGIT_SIZE 4

//mi baso sull'ottava che parte dal DO
const static boolean TestAlteredNote[] PROGMEM = {false, true, false, true, false, false, true, false, true, false, true, false};

//lo shift consiste che l'ottava parte dal LA. (la 21° è A0), parto da li a contare
const static boolean TestAlteredNote_Shifted[] PROGMEM = {false, true, false, false, true, false, true, false, false, true, false, true};
const static uint8_t BlackNote_To_WhiteNote_Shifted[] PROGMEM = {0,0,1,2,2,3,3,4,5,5,6,6};

const static uint8_t Colors [ColorAvailable][3] PROGMEM =  {
    
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

void static inline LoadColorFromFlash(register uint8_t index, register uint8_t *pRED, register uint8_t *pGREEN, register uint8_t *pBLUE) {
    
    //index = index % COLOR_AVAILABLE;
    
    *pRED   = pgm_read_byte(&(Colors[index][0]));
    *pGREEN = pgm_read_byte(&(Colors[index][1]));
    *pBLUE  = pgm_read_byte(&(Colors[index][2]));
}

/*
void LoadStringFromFlash(uint16_t Position, const char* array[]) {
  strcpy_P(Stringsbuffer, (char*)pgm_read_word(&(array[Position])));
}
*/


typedef struct Nota
{
    uint8_t NotaNumber;
    uint8_t Velocity; //MAX 127
    uint8_t LED_Index;
    bool Pressed;

}Nota;

class LED
{
    private:
        inline uint8_t GetNote_Number() {
            return ((this->LedFlags >> 1) & 0x03);
        }
    public:

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
        int8_t Trasnspose = 0;//+-127

        uint8_t Piano_LED_Animation = NORMAL_EFFECT;
        uint8_t Piano_LED_ColorMode = STATIC_COLOR; 
        uint8_t Piano_LED_ColorIndex = 0;


        uint8_t redColorValue;
        uint8_t greenColorValue;
        uint8_t blueColorValue;
        uint16_t hueValue = 0;

        boolean switch1_state = false;
        boolean switch2_state = false;
        boolean switch3_state = false;

        uint64_t debounce_time1 = 400;
        uint64_t last_debounce_time1 = millis() - debounce_time1;
        

        Nota PianoNote[TOTAL_NOTE];
        LED  PianoLED[(int)TOTAL_LED];
   
        uint8_t ToWhiteNote[NotePerOttava] = {0,0,1,1,2,3,3,4,4,5,5,6};

 

        inline boolean isOn(register uint8_t LED_index) {
            return ((PianoLED[LED_index].LedFlags & LED_STATE_FLAG) == 0x01);
        }

        inline boolean isOff(register uint8_t LED_index) {
            return ((PianoLED[LED_index].LedFlags & LED_STATE_FLAG) == 0x00);
        }

        inline void turnOn(register uint8_t LED_index) {
            
            if(Piano_LED_ColorMode == STATIC_COLOR)
                LED_Interface->SetLedColor(LED_index, redColorValue, greenColorValue, blueColorValue);
            else
                LED_Interface->SetLedColor_by_HUE(LED_index, hueValue);
            
            PianoLED[LED_index].LedFlags |= 0x01;
            
        }

        inline void turnOff(register uint8_t LED_index) {
            LED_Interface->SetLedColor(LED_index, 0x00, 0x00, 0x00);
            PianoLED[LED_index].LedFlags &= 0xFE;
        }

        inline void clear() {
            LED_Interface->clear();  
        }
        

        //aggiorna tutti i LED, impostando il colore presente nelle variabili
        void inline UpdateLED_Color() {

            for(register uint8_t LED_index = 0; LED_index < TOTAL_LED; LED_index++) {
                if(isOn(LED_index)) {
                    turnOff(LED_index);                 
                    delayMicroseconds(100);
                }/*else if(LED_index <= 32) {
                    turnOff(LED_index);
                    delayMicroseconds(400);
                }*/
            }
            
        }

        //Carica il colore predefinito salvato nella EEPROM e lo imposto sui LED
        void inline Load_and_Update_LED_Color() {
            if(Piano_LED_ColorMode != STATIC_COLOR)
                Piano_LED_ColorMode = STATIC_COLOR;

            LoadColorFromFlash(Piano_LED_ColorIndex, &this->redColorValue, &this->greenColorValue, &this->blueColorValue);     
            UpdateLED_Color();
        }

        float NoteToLed_Conversion(uint8_t note);
        uint8_t Calculate_Associated_LEDs(uint8_t note);
        

    public:

        Piano(uint8_t pin);
        void PressNote(uint8_t note, uint8_t velocity);
        void RelaseNote(uint8_t note);
        void UpdateNote(uint8_t note);
        void PrintInformation(Nota *p);
        void UpDateLED(const register uint8_t LED_index);
        void Print();

        void function_Button1(register boolean state);
        void function_Button2(register boolean state);
        void function_Button3(register boolean state);
        
        void refresh() {LED_Interface->refresh();}
        void UpdateHue() {hueValue++;}

        void Forceclear() {
            LED_Interface->clear(); 
            for(register uint8_t i = 0; i < TOTAL_LED; i++) {
               turnOff(i);
            }
        }

        void Load_nextColor() {
            Piano_LED_ColorIndex = (Piano_LED_ColorIndex + 1) % COLOR_AVAILABLE; 
            if(Piano_LED_ColorMode != STATIC_COLOR)
                Piano_LED_ColorMode = STATIC_COLOR;

            LoadColorFromFlash(Piano_LED_ColorIndex, &this->redColorValue, &this->greenColorValue, &this->blueColorValue);
        }

        void Load_previousColor() {
            Piano_LED_ColorIndex = ((Piano_LED_ColorIndex == 0) ? (COLOR_AVAILABLE - 1) : (Piano_LED_ColorIndex - 1));
            if(Piano_LED_ColorMode != STATIC_COLOR)
                Piano_LED_ColorMode = STATIC_COLOR;

            LoadColorFromFlash(Piano_LED_ColorIndex, &this->redColorValue, &this->greenColorValue, &this->blueColorValue);
        }


        //imposta il colore successivo
        void nextColor() {
            Piano_LED_ColorIndex = (Piano_LED_ColorIndex + 1) % COLOR_AVAILABLE; 
            Load_and_Update_LED_Color();
        }

        //imposta il colore precedente
        void previousColor() {
            Piano_LED_ColorIndex = ((Piano_LED_ColorIndex == 0) ? (COLOR_AVAILABLE - 1) : (Piano_LED_ColorIndex - 1));
            Load_and_Update_LED_Color();
        }

        //imposta il colore (predefinito) presente all'indice specificato
        void SetColor(uint8_t index) {
            Piano_LED_ColorIndex = (index % COLOR_AVAILABLE);           
            Load_and_Update_LED_Color();
        }

        //imposta un colore a scelta.
        void SetColor(uint8_t R, uint8_t G, uint8_t B) {
            if(Piano_LED_ColorMode != STATIC_COLOR) Piano_LED_ColorMode = STATIC_COLOR;           
            this->redColorValue   = R;
            this->greenColorValue = G;
            this->blueColorValue  = B;
            UpdateLED_Color();
        }

        //imposta i colori RGB
        void RGB_Color() {
            if(Piano_LED_ColorMode != DYNAMIC_RGB_COLOR)
                Piano_LED_ColorMode = DYNAMIC_RGB_COLOR;
        }

        //imposta un'effetto
        void setEffect(uint8_t val) {
            this->Piano_LED_Animation = val;
        }


        void IncrementTranspose() {
            if(this->Trasnspose < 12)
                this->Trasnspose++;

            //shift note
        }

        void DecrementTranspose() {
            if(this->Trasnspose > -12)
                this->Trasnspose--;
            //shift note
        }

        void ResetTranspose() {
            this->Trasnspose = 0;
            //shift note
        }
};

//Note Piano::PianoNote[TOTAL_NOTE]



#endif // PIANO_H
