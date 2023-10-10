#include "Piano.h"







Piano::Piano(uint8_t pin) 
{
  LED_Interface = new WS2812_interface();
  LED_Interface->init(TOTAL_NOTE, pin, this->LED_MAX_Brightness);

  //resetto il colore
  SetColor(0);

  
  

  //per tutte le note che possiede il PianoForte
  for(register uint8_t i = 0; i < TOTAL_NOTE; i++)                                          
  {
    //inizializzo i parametri della Nota
    register Nota *pNota = &PianoNote[i];//(Nota*)malloc(sizeof(Nota));                            
    pNota->NotaNumber = i + NoteOffset;
    pNota->Pressed = false;
    pNota->Velocity = 0;
    pNota->LED_Index = 0;
    
    //calcolo dove è situata la nota. (considero l'ottava che parte dal LA)
    register uint8_t octave = i / 12;        
    register uint8_t octaveNote = i % 12;
    register boolean isAltered = pgm_read_byte(&(TestAlteredNote_Shifted[octaveNote]));
    register uint8_t octaveWhiteElement = pgm_read_byte(&(BlackNote_To_WhiteNote_Shifted[octaveNote]));

    //calcolo dove inizia e finisce la nota
    float NoteStart_point = (octave*WHITE_NOTE_PER_OCTAVE + octaveWhiteElement)*PIANO_WHITE_NOTE_LENGHT + ((isAltered) ? BLACK_NOTE_OFFSET_FROM_WHITE_NOTE : 0);
    float NoteEnd_point = NoteStart_point + ((isAltered) ? PIANO_WHITE_NOTE_LENGHT : PIANO_WHITE_NOTE_LENGHT);//PIANO_BLACK_NOTE_LENGHT


    //cerco tutti i LED che sono nei limiti della Nota
    for(register uint8_t j = 0; j < TOTAL_LED; j++) 
    {
      float LED_Start_point = LED_LENGHT*j;
      float LED_End_point = LED_Start_point + LED_LENGHT;
      float distanceScrap = ((isAltered) ? PIANO_WHITE_NOTE_LENGHT/3 : PIANO_WHITE_NOTE_LENGHT/3);

      //è inutile che calcolo anche quelli successivi
      //if(LED_End_point > NoteEnd_point)
      //  break;

      //Le condizioni
      boolean A = ((LED_End_point >= (NoteStart_point + distanceScrap)) && (LED_End_point <= NoteEnd_point));
      boolean B = ((LED_Start_point >= NoteStart_point) && (LED_Start_point <= NoteEnd_point - distanceScrap));

      //il LED è nei confini della nota
      if(A || B) {
        register LED *pLED = &PianoLED[j];    //prendo il puntatore e lo invio alla funzione
        pLED->addNote(pNota);

        if(pNota->LED_Index == 0) {
          pNota->LED_Index = j;
        } else {
          pNota->LED_Index |= 0x80;
        }
      }
    }
  }
}

void ::Piano::function_Button1(register boolean state) 
{
  if((millis() - this->last_debounce_time1) > this->debounce_time1) {
    this->last_debounce_time1 = millis();
    this->switch1_state = state;

    if(this->switch1_state == false)
      return;

    switch(Piano_LED_Animation) 
    {
      case NORMAL_EFFECT: 
      case NO_DELAY_EFFECT:
      {
        if(this->switch3_state) {
          Load_previousColor();
        }else {
          Load_nextColor();
        }
        break;
      }
      case RANDOM_ON_FORCE_EFFECT: 
      {

        break;
      }
    }
  }
}



void Piano::PressNote(uint8_t note, uint8_t velocity) 
{
    note += Trasnspose;

    //il 21 è lo 0
    if(note < 21) note = NOTE_START_OFFSET;
    else if(note > NOTE_END_WITH_OFFSET) note = NOTE_END_WITH_OFFSET;

    note = note - NOTE_START_OFFSET;

    PianoNote[note].Pressed = true;
    PianoNote[note].Velocity = velocity;

    if(Piano_LED_Animation == RANDOM_ON_FORCE_EFFECT && velocity > 108) {
      SetColor(random(COLOR_AVAILABLE));
    }

}

void Piano::RelaseNote(uint8_t note)
{
    note += Trasnspose;
    if(note < 21) note = NOTE_START_OFFSET;
    else if(note > NOTE_END_WITH_OFFSET) note = NOTE_END_WITH_OFFSET;

    note = note - NOTE_START_OFFSET;
    PianoNote[note].Pressed = false;

}


void Piano::UpDateLED(const register uint8_t LED_index) 
{
  
    switch(Piano_LED_Animation) 
    {
      case NONE_EFFECT: {

        if(isOn(LED_index)) {
          turnOff(LED_index);
        }
        break;
      }
      case NO_DELAY_EFFECT:
      case NORMAL_EFFECT: 
      case RANDOM_ON_FORCE_EFFECT: 
      {

        //il LED è acceso ?
        if(isOn(LED_index)) 
        {
          //se non ci sono note premute
          if(!PianoLED[LED_index].check_turnOn()) 
          { 
            //se il tempo è finito
            if(Piano_LED_Animation == NO_DELAY_EFFECT || Piano_LED_Animation == RANDOM_ON_FORCE_EFFECT || PianoLED[LED_index].DissolvenceTime == 0) {
              turnOff(LED_index);
            } 
            //altrimenti decremento il tempo
            else {

            }
          }
        }
        //Posso accendere il LED ?
        else if(PianoLED[LED_index].check_turnOn()) {
            turnOn(LED_index);
        }
        break;
      }
      
    } 
}


void Piano::Print()
{
    DEBUG_PORT.print(F("Toltal white note: ")); DEBUG_PORT.println(PIANO_TOTAL_WHITE_NOTE);
    DEBUG_PORT.print(F("Piano lenght: "));      DEBUG_PORT.println((float)PIANO_LENGHT);
    DEBUG_PORT.print(F("Note lenght: "));       DEBUG_PORT.println((float)PIANO_NOTE_LENGHT);
    DEBUG_PORT.print(F("Toltal LED: "));        DEBUG_PORT.println((int)TOTAL_LED);

    for(uint8_t i = 0; i < TOTAL_NOTE; i++) 
    {
        Nota *pNota = &PianoNote[i];

        PrintInformation(pNota);
        DEBUG_PORT.print(F(" |Nota Address: &"));
        DEBUG_PORT.print((unsigned int)pNota);
        DEBUG_PORT.print(F("  | | "));

        if(i < TOTAL_LED - 1) 
        {
          LED *pLED = &PianoLED[i];

          DEBUG_PORT.print(F(" &"));
          DEBUG_PORT.print((unsigned int)pLED);
          DEBUG_PORT.print(F("  LED "));
          DEBUG_PORT.print(i);
          DEBUG_PORT.print(' ');

          if(i < 10) 
            DEBUG_PORT.print(F("  : ["));
          else
            DEBUG_PORT.print(F(" : ["));

          pLED->PrintAddress();
          DEBUG_PORT.print(']');;
        }    
        Serial.println();
    }
}

void Piano::PrintInformation(Nota *p)
{
  DEBUG_PORT.print(F(" Nota numero: ["));
  DEBUG_PORT.print(p->NotaNumber);

  if(p->NotaNumber < 10) 
    DEBUG_PORT.print(' ');
  if(p->NotaNumber < 100) 
    DEBUG_PORT.print(' ');

  DEBUG_PORT.print(F("] => LED: ["));
  DEBUG_PORT.print(p->LED_Index & 0x7F);

  if((p->LED_Index & 0x7F) < 10) 
    DEBUG_PORT.print(' ');


  if(p->LED_Index & 0x80 == 0x80) 
  {
    DEBUG_PORT.print(F(", "));
    DEBUG_PORT.print((p->LED_Index & 0x7F) + 1);

    if(((p->LED_Index & 0x7F) + 1) < 10) 
      DEBUG_PORT.print(' ');
  }
  else {
    DEBUG_PORT.print(' ');
    DEBUG_PORT.print(' ');
    DEBUG_PORT.print(' ');
    DEBUG_PORT.print(' ');
  }
  DEBUG_PORT.print(']');
}

//NOTE_START_OFFSET corrisponde al valore 0
/*uint8_t Piano::Calculate_Associated_LEDs(uint8_t note) 
{ 
  register uint8_t octave = note / 12;
  register uint8_t octaveNote = note % 12;
  register uint8_t LED_INDEX;

  register boolean isAltered = pgm_read_byte(&(TestAlteredNote_Shifted[octaveNote]));
  register uint8_t octaveWhiteElement = pgm_read_byte(&(BlackNote_To_WhiteNote_Shifted[octaveNote]));
  
  //calcolo dove inizia e finisce la nota
  float NoteStart = (octave*WHITE_NOTE_PER_OCTAVE + octaveWhiteElement)*PIANO_WHITE_NOTE_LENGHT + ((isAltered) ? BLACK_NOTE_OFFSET_FROM_WHITE_NOTE : 0);
  float NoteEnd = NoteStart + ((isAltered) ? BLACK_NOTE_OFFSET_FROM_WHITE_NOTE : PIANO_BLACK_NOTE_LENGHT);

  return LED_INDEX;
}*/

/*float Piano::NoteToLed_Conversion(uint8_t note) 
{
    uint16_t ottava = note/12 - 1;      //per capire in quale ottava sono
    uint16_t NoteNumber = note%12;      //per capire quale nota dell'ottava è
    float position = 0.0;               

    //Serial.println(ottava);
    //Serial.println(NoteNumber);

    if(AlteredArray[NoteNumber]) {
      NoteNumber --;
      position = position + PIANO_NOTE_LENGHT/2;
    }
      
    NoteNumber = ToWhiteNote[NoteNumber];

    #ifdef Debug1
      Serial.println(NoteNumber);

      position = position + (NoteNumber + 1) * NoteLenght;
      Serial.println(position);

      position = position + ottava * offset1;
      Serial.println(position);

      position = position - offset2;
    #else
      position += (NoteNumber + 1) * PIANO_NOTE_LENGHT;
      position += ottava * offset1 - offset2;
    #endif

    return position;
}*/



LED::LED()
{
  
}

void LED::addNote(Nota *p) {

  if(this->FistNotePointer == NULL) {
    this->FistNotePointer = p;
  }

  uint8_t element = ( this->LedFlags >> 1) & 0x03;
  element++;

  this->LedFlags &= 0b11111001;
  this->LedFlags |= (element << 1);
  //this->LedFlags = (this->LedFlags & 0b11111001) | (((this->LedFlags >> 1) & 0x03) + 1);
}

void LED::PrintAddress() 
{
  if(this->FistNotePointer == NULL) 
    return;
  
  Nota *p = this->FistNotePointer;
  

  for(int i = 0; i < 3; i++) 
  {
    if(i < this->GetNote_Number()) {
      int *p2 = (int *) &p;
      DEBUG_PORT.print(F(" &"));
      DEBUG_PORT.print((unsigned int)(*p2));
      p++;
    } 
    else {
      for(int j = 0; j < ADDESS_DIGIT_SIZE + 2; j++) {
        DEBUG_PORT.print(' ');
      }
    }

    if(i < 3 - 1)
      DEBUG_PORT.print(',');
      DEBUG_PORT.print(' ');
  }
}


void LED::Update()
{
 
}

//verifico se posso accendere il LED
//7810, 7814, 7818 => che sono in sequenza
//cercp se esiste almeno una Nota che è stata premuta
bool LED::check_turnOn()
{
  register Nota *p = this->FistNotePointer;

  for(register int i = 0; i < ((this->LedFlags >> 1) & 0x03); i++) {
    if(p->Pressed) return true;
    p++; //incremento il puntatore alla locazione sucessiva
  }
  return false;
}

/*Nota::Nota(uint8_t NotaNumber) {
  this->NotaNumber = NotaNumber;
}*/



/*void Nota::PrintInformation()
{
  

}*/