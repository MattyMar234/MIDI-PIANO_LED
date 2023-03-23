#ifndef HARDWARETIMER_H
#define HARDWARETIMER_H

#include <Arduino.h>

#define TIMER0_MAX_COMP_VAL 255
#define TIMER1_MAX_COMP_VAL 65535
#define TIMER2_MAX_COMP_VAL 255
#define XTAL_FREQ 16000000
#define NO_CLOCK_SOURCE 0
#define EXTERNAL_FALLING 1
#define EXTERNAL_RISING 2
#define TIMER_MODE 1
#define DISABLE_INTERRUPT 0
#define INTERRUPT_ON_OVERFLOW 1
#define INTERRUPT_ON_COMPA 2
#define INTERRUPT_ON_COMPB 3
#define INTERRUPT_ON_COMPB 4




class TimerCounter_Base {

    protected:
        static uint8_t Mode;
        static uint8_t prescaler;

        static inline boolean setAsTimer(uint8_t block, uint32_t freq, uint8_t interruptMode, uint16_t *pPerscalers, uint8_t n) {
            uint64_t compareMatchReg = 0;
            uint8_t i;
            uint32_t COMP_reg_value;

            

            switch (block)
            {
                case 0: {
                    COMP_reg_value = TIMER0_MAX_COMP_VAL;
                    TCCR0A = 0x00;          // set entire TCCR0A register to 0
                    TCCR0B = 0x00;          // set entire TCCR0B register to 0
                    TCNT0  = 0x00;          //initialize counter value to 0
                    TIMSK0 = 0x00;          //clear interrupt flags
                    break;
                }
                case 1: {
                    COMP_reg_value = TIMER1_MAX_COMP_VAL;
                    TCCR1A = 0x00;          // set entire TCCR1A register to 0
                    TCCR1B = 0x00;          // set entire TCCR1B register to 0
                    TCCR1C = 0x00;          // set entire TCCR1C register to 0
                    TCNT1  = 0x00;          //initialize counter value to 0 TCNT1H & TCNT1L
                    TIMSK1 = 0x00;          //clear interrupt flags
                    break;
                }
                case 2: {
                    COMP_reg_value = TIMER2_MAX_COMP_VAL;
                    TCCR2A = 0x00;          // set entire TCCR2A register to 0
                    TCCR2B = 0x00;          // set entire TCCR2B register to 0
                    TCNT2  = 0x00;          //initialize counter value to 0
                    TIMSK2 = 0x00;          //clear interrupt flags
                    break;
                }
        
                default:
                    break;
            } 

            // ==================== [Prescaler] ====================//
            //scandisco tutti i prescaler che ho a disposizione
            for(i = 1; i < n + 2; i++) {
                if(i == n + 1) {
                    return false;
                }
                compareMatchReg = (XTAL_FREQ/(freq*(*pPerscalers))) - 1;      //calolo il valore del comparatore con il seguente prescaler
                pPerscalers++;

                if(compareMatchReg <= COMP_reg_value)                               //se è minore del valore massimo ammissibile, interrompo il ciclo
                    break;
            } 

            
            Mode = TIMER_MODE;
            prescaler = i;

            switch (block)
            {
                case 0: {
                    TCCR0A |= (1 << WGM01);         // turn on CTC mode
                    OCR0A = compareMatchReg;
                    TCCR0B |= i;
                    break;
                }

                case 1: {
                    TCCR1B |= (1 << WGM12);         // turn on CTC mode
                    OCR1A = compareMatchReg;
                    TCCR1B |= i;
                    break;
                }

                case 2: {
                    OCR2A = compareMatchReg;
                    TCCR2B |= i;
                    break;
                }
            
                default:
                    break;
            }

            //==================== [INTERRUPT] ====================//
            uint8_t temp;

            switch (interruptMode)
            {
                case INTERRUPT_ON_OVERFLOW: {
                    temp = 0x01;    //TOIEx
                    break;
                }
                case INTERRUPT_ON_COMPA: {
                    temp = 0x02;    //OCIExA
                    break;
                }
                case INTERRUPT_ON_COMPB: {
                    temp = 0x04;    //OCIExB
                    break;
                }
                default:
                    return false;
                    break;
            }

            if(block == 0) 
                TIMSK0 = temp; 
            else if(block == 1)
                TIMSK1 = temp;
            else if(block == 2)
                TIMSK2 = temp;

            return true;
           
        }

        static bool setTimerInputSource(uint8_t block, uint8_t source)
        {
            switch (source)
            {
                case NO_CLOCK_SOURCE: {
                    if(block == 0) 
                        TCCR0B &= 0b11111000; 
                    else if(block == 1)
                        TCCR1B &= 0b11111000;
                    else if(block == 2)
                        TCCR2B &= 0b11111000;

                    return true;
                    break;
                }                    
                case EXTERNAL_FALLING: {
                    if(block == 0) {
                        TCCR0B &= 0b11111000;
                        TCCR0B |= 0b00000110;
                    }
                    else if(block == 1) {
                        TCCR1B &= 0b11111000;
                        TCCR1B |= 0b00000110;
                    }
                    else if(block == 2){
                        TCCR2B &= 0b11111000;
                        TCCR2B |= 0b00000110;
                    }
                    
                    return true;
                    break;
                }
                    
                case EXTERNAL_RISING: {
                    if(block == 0) {
                        TCCR0B &= 0b11111000;
                        TCCR0B |= 0b00000111;
                    }
                    else if(block == 1) {
                        TCCR1B &= 0b11111000;
                        TCCR1B |= 0b00000111;
                    }
                    else if(block == 2){
                        TCCR2B &= 0b11111000;
                        TCCR2B |= 0b00000111;
                    }
                    
                    return true;
                    break;
                }
                default:
                    return false;
                    break;
            }
        }


        static boolean StopTimer(uint8_t block) 
        {
            if(Mode != TIMER_MODE) {
                return false;
            }

            setTimerInputSource(block, NO_CLOCK_SOURCE);
            return true;
        }

        static boolean StartTimer(uint8_t block) 
        {
            if(Mode != TIMER_MODE) {
                return false;
            }

            if(block == 0) {
                TCCR0B &= 0b11111000;
                TCCR0B |= prescaler;
            }
            else if(block == 1) {
                TCCR1B &= 0b11111000;
                TCCR1B |= prescaler;
            }
            else if(block == 2){
                TCCR2B &= 0b11111000;
                TCCR2B |= prescaler;
            }
            return true;
        }

        
};

uint8_t TimerCounter_Base::Mode = 0;
uint8_t TimerCounter_Base::prescaler = 0;


class Hardware_TimerCounter0 : public TimerCounter_Base 
{
    private:
    

    public:

        static boolean setAsTimer(uint32_t freq, uint8_t interruptMode) 
        {
            uint16_t Perscalers[] = {1,8,64,256,1024};
            return TimerCounter_Base::setAsTimer(0, freq, interruptMode, &Perscalers[0], 5);
              
        }
};

class Hardware_TimerCounter1 : public TimerCounter_Base 
{
    private:
    

    public:

        static boolean setAsTimer(uint32_t freq, uint8_t interruptMode) 
        {
            uint16_t Perscalers[] = {1,8,64,256,1024};
            return TimerCounter_Base::setAsTimer(1, freq, interruptMode, &Perscalers[0], 5);
        }

};

#endif //HARDWARETIMER_H