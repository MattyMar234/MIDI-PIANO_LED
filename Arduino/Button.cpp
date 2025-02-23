#include "Button.h"


Button::Button(uint8_t pin, uint8_t mode, unsigned long debounce_time) 
{

    this->PIN = pin;
    this->Mode = mode;
    this->debounce_time = debounce_time;
    last_debounce_time = millis() - debounce_time;
    
    pinMode(pin, INPUT);
    last_state   = digitalRead(pin);
    button_state = digitalRead(pin);
}

bool Button::getState() {
    return digitalRead(this->PIN);
}

uint8_t Button::getPin() {
    return this->PIN;
}

void Button::setPin(uint8_t pin) {
    this->PIN = pin;
}

void Button::setDebounce_time(unsigned long debounce_time) {
    this->debounce_time = debounce_time;
}

unsigned long Button::getDebounce_time() {
    return this->debounce_time;
}

bool Button::ButtonFunctionAvailable()
{
    //se è passato il tempo eseguo
    if((millis() - last_debounce_time) > debounce_time)
    {
        bool result = false;
        this->button_state = digitalRead(this->PIN);

        switch (this->Mode)
        {

        //change
        case ButtonChange:
            if(this->button_state != this->last_state) {
                this->last_state = this->button_state;
                result = true;
            }
            break;
        
        //falling
        case ButtonFalling:
            if(this->button_state != this->last_state) {
                this->last_state = this->button_state;

                if(button_state == LOW) {
                    result = true;
                }     
            }
            break;

        //rising
        case ButtonRising:
            if(this->button_state != this->last_state) {
                this->last_state = this->button_state;

                if(button_state == HIGH) {
                    result = true;
                }     
            }
            break;
        }
        
        if(result) {
            last_debounce_time = millis();
        } 
        return result;
    } 
    else {
        return false;
    }
}