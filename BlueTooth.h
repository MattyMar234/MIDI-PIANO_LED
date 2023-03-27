#ifndef BLUETOOTH_H
#define BLUETOOTH_H

#include <Arduino.h>
#include <SoftwareSerial.h>
#include "HardwareSerial.h"

#define SW_SERIAL_MODE 0
#define HW_SERIAL_MODE 1
#define SERIAL0_MODE 2
#define SERIAL1_MODE 3
#define SERIAL2_MODE 4

#define START_COMMAND '/'
#define END_COMMAND '\n'

template <typename SerialType>
class Bluetooth
{
    private:
        SerialType *BTserial = NULL;
        uint8_t ComunicationMode;
        uint8_t rxPin;
        uint8_t txPin;

    public:
        //softwareSerial
        Bluetooth(uint8_t rxPin, uint8_t txPin, boolean inverse_logic, uint64_t speed) {
            //this->BTserial = new HardWareSerial1(rxPin, txPin, inverse_logic);
            ComunicationMode = SW_SERIAL_MODE;
        }

        //hardwareSerial
        Bluetooth()  {
            
        }

        boolean begin(uint64_t USART_BAUDRATE) 
        {
            if(this->BTserial == NULL)
                this->BTserial = new SerialType();

            ComunicationMode = HW_SERIAL_MODE;
            BTserial->init(USART_BAUDRATE);
        }

        boolean attachInterrupt_RX(void (*userFunc)(void)) {
            return BTserial->attachInterrupt(userFunc, INTERRUPT_ON_RX_COMPLETE);
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