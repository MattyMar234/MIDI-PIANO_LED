#include "Piano.h"







Piano::Piano(uint8_t pin) 
{
    LED_Interface = new WS2812_interface();
    LED_Interface->init(TOTAL_NOTE, pin, this->LED_MAX_Brightness);
    //WS2812_interface::init(TOTAL_LED, pin);

    

    
    
    for(register uint8_t i = 0; i < TOTAL_NOTE; i++)                                          //per tutte le note che possiede il PianoForte
    {
        //Calcolo i led corrispondenti alla Nota
        float   floatValue = NoteToLed_Conversion(i + NoteOffset)/LED_LENGHT - 1;             //calcolo la posizione in floating point
        uint8_t IntegerValue = (uint8_t) floatValue; 


        // ================== Inizializzazione Nota ================== //
        Nota *pNota = &PianoNote[i];//(Nota*)malloc(sizeof(Nota));                            //creao una oggetto puntatore nota e lo inizializzo

        pNota->NotaNumber = i + NoteOffset;
        pNota->Pressed = false;
        pNota->Velocity = 0;
        
        //verifico la soglia
        if((floatValue - IntegerValue) >= 0.55)
            pNota->LED_Index = IntegerValue | 0x80;
        else
            pNota->LED_Index = IntegerValue & 0x7F;
                                                            
        
        // ================== Inizializzazione LED ================== //
        //eseguo 2 iterazioni se la nota ha due LED
        for(register uint8_t j = 0; j < ((pNota->LED_Index & 0x80 == 0x80) ? 2 : 1); j++) 
        {
          register LED *pLED = &PianoLED[(pNota->LED_Index & 0x7F) + j];
          pLED->addNote(pNota);
        }
    }
}

void Piano::refresh() {
  LED_Interface->refresh();
}

void Piano::PressNote(uint8_t note, uint8_t velocity) 
{
    note += Trasnspose;

    //il 21 è lo 0
    if(NOTE_START_OFFSET < 21) note = NOTE_START_OFFSET;
    else if(note > NOTE_END_WITH_OFFSET) note = NOTE_END_WITH_OFFSET;

    note = note - NOTE_START_OFFSET;

    PianoNote[note].Pressed = true;
    PianoNote[note].Velocity = velocity;

}

void Piano::RelaseNote(uint8_t note)
{
    note += Trasnspose;
    if(NOTE_START_OFFSET < 21) note = NOTE_START_OFFSET;
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
      {

        //il LED è acceso ?
        if(isOn(LED_index)) 
        {
          //se non ci sono note premute
          if(!PianoLED[LED_index].check_turnOn()) 
          { 
            //se il tempo è finito
            if(Piano_LED_Animation == NO_DELAY_EFFECT || PianoLED[LED_index].DissolvenceTime == 0) {
              turnOff(LED_index);
            } 
            //altrimenti decremento il tempo
            else {

            }
          }
        }
        //Posso accendere il LED ?
        else if(PianoLED[LED_index].check_turnOn()) {
            turnOn(LED_index, 0xFF, 0x00, 0x00);
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

float Piano::NoteToLed_Conversion(uint8_t note) 
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
}



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