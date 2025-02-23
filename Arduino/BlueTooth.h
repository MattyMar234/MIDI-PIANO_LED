#ifndef BLUETOOTH_H
#define BLUETOOTH_H

#include <Arduino.h>
#include "HardwareSerial.h"

#define SERIAL0_MODE 2
#define SERIAL1_MODE 3
#define SERIAL2_MODE 4

#define START_COMMAND '/'
#define END_COMMAND '\n'

template <typename Hardware_SerialType>
class Bluetooth
{
    private:
        Hardware_SerialType *BTserial = NULL;
        boolean connected = false;
        boolean INT_Connected_available = false;
        boolean INT_RX_available = false;
        boolean INT_TX_available = false;
        
    public:

        Bluetooth()  {
            
        }

        boolean getState() {
          return connected;
        }

        void setState(boolean s) {
          connected = s;
        }


        boolean begin(uint64_t USART_BAUDRATE) 
        {
          connected = false;

          if(this->BTserial == NULL)
            this->BTserial = new Hardware_SerialType();
          else {
            free(this->BTserial);
            this->BTserial = new Hardware_SerialType();
          }

            BTserial->init(USART_BAUDRATE);

          return true;
        }

        boolean attachInterrupt_RX(void (*userFunc)(void)) {
            INT_RX_available = true;
            return BTserial->attachInterrupt(userFunc, INTERRUPT_ON_RX_COMPLETE);
        }

        boolean attachInterrupt_BT_Status(void (*userFunc)(void), uint8_t interruptPin) {
            INT_Connected_available = true;
            pinMode(interruptPin, INPUT);
            attachInterrupt(digitalPinToInterrupt(interruptPin), userFunc, CHANGE);
        }

        uint8_t read() {
          return BTserial->read();
        }

        void write(uint8_t data) {
          BTserial->write(data);
        }

        boolean available() {
          return BTserial->available();
        }

        

};
        

#endif //BLUETOOTH_H