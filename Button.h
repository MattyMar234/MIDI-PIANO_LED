#ifndef BUTTON_H
#define BUTTON_H

#include <arduino.h>


class Button
{
    private:
        uint8_t PIN;
        uint8_t Mode;
        bool last_state;
        bool button_state;
        unsigned long last_debounce_time;
        unsigned long debounce_time;

    public:

        static const uint8_t ButtonChange = 0;
        static const uint8_t ButtonFalling = 1;
        static const uint8_t ButtonRising = 2;

        Button(uint8_t pin, uint8_t mode, unsigned long debounce_time);
        
        bool getState();
        uint8_t getPin();
        void setPin(uint8_t pin);
        void setDebounce_time(unsigned long debounce_time);
        unsigned long getDebounce_time();
        bool ButtonFunctionAvailable();

};


#endif