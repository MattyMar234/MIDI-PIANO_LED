#ifndef HARDWARE_SWERIAL_H
#define HARDWARE_SWERIAL_H

#include <Arduino.h>

#define MYUBRR (((F_CPU / (USART_BAUDRATE * 16UL))) - 1)
#define INTERRUPT_ON_RX_COMPLETE 1
#define INTERRUPT_ON_TX_COMPLETE 2
#define INTERRUPT_ON_DATA_REGISTER_EMPTY 3

typedef void (*voidFuncPtr)(void);

// 168 and 328 Arduinos
#if defined(__AVR_ATmega168__) ||defined(__AVR_ATmega168P__) ||defined(__AVR_ATmega328P__)
    #define SERIAL_INTERRUPT_VECTORS 3
// Mega 1280 & 2560
#elif defined(__AVR_ATmega1280__) || defined(__AVR_ATmega2560__) || defined(ARDUINO_AVR_MEGA2560)
    #define SERIAL_INTERRUPT_VECTORS 12
#endif




//Nota: static => visibilità solo in questo file
static void nothing(void) {}

//inizializzo l'array con n puntatori a una funzione che non esegue nulla
static volatile voidFuncPtr intFunc[SERIAL_INTERRUPT_VECTORS] = {
    #if SERIAL_INTERRUPT_VECTORS > 12 
        nothing,
    #endif
    #if SERIAL_INTERRUPT_VECTORS > 11
        nothing,
    #endif
    #if SERIAL_INTERRUPT_VECTORS > 10
        nothing,
    #endif
    #if SERIAL_INTERRUPT_VECTORS > 9
        nothing,
    #endif
    #if SERIAL_INTERRUPT_VECTORS > 8
        nothing,
    #endif
    #if SERIAL_INTERRUPT_VECTORS > 7
        nothing,
    #endif
    #if SERIAL_INTERRUPT_VECTORS > 6
        nothing,
    #endif
    #if SERIAL_INTERRUPT_VECTORS > 5
        nothing,
    #endif
    #if SERIAL_INTERRUPT_VECTORS > 4
        nothing,
    #endif
    #if SERIAL_INTERRUPT_VECTORS > 3
        nothing,
    #endif
    #if SERIAL_INTERRUPT_VECTORS > 2
        nothing,
    #endif
    #if SERIAL_INTERRUPT_VECTORS > 1
        nothing,
    #endif
    #if SERIAL_INTERRUPT_VECTORS > 0
        nothing,
    #endif
};

#define IMPLEMENT_ISR(vect, interrupt) \
  ISR(vect) { \
    intFunc[interrupt](); \
  }

  // 168 and 328 Arduinos
#if defined(__AVR_ATmega168__) ||defined(__AVR_ATmega168P__) || defined(__AVR_ATmega328P__)
    
    //IMPLEMENT_ISR(USART_RX_vect, 0)
    //IMPLEMENT_ISR(USART_UDRE_vect, 1)
    //IMPLEMENT_ISR(USART_TX_vect, 2)

    // Mega 1280 & 2560
#endif

#if defined(__AVR_ATmega1280__) || defined(__AVR_ATmega2560__)

    //IMPLEMENT_ISR(USART0_RX_vect, 0)
    //IMPLEMENT_ISR(USART0_UDRE_vect, 1)
    //IMPLEMENT_ISR(USART0_TX_vect, 2)

    IMPLEMENT_ISR(USART1_RX_vect, 3)
    IMPLEMENT_ISR(USART1_UDRE_vect, 4)
    IMPLEMENT_ISR(USART1_TX_vect, 5)

    IMPLEMENT_ISR(USART2_RX_vect, 6)
    IMPLEMENT_ISR(USART2_UDRE_vect, 7)
    IMPLEMENT_ISR(USART2_TX_vect, 8)

    IMPLEMENT_ISR(USART3_RX_vect, 9)
    IMPLEMENT_ISR(USART3_UDRE_vect, 10)
    IMPLEMENT_ISR(USART3_TX_vect, 11)

#endif




template <typename pRegister, uint8_t K>
class Interface_HardwareSerial
{
    private:
        pRegister UCSRnA;
        pRegister UCSRnB;
        pRegister UCSRnC;
        pRegister UDRn;
        pRegister UBRRnH;
        pRegister UBRRnL;

        uint8_t PrescalerValue = 16;

    public:
        Interface_HardwareSerial(pRegister UCSRA, pRegister UCSRB, pRegister UCSRC, pRegister UDR, pRegister UBRRH, pRegister UBRRL) {
            this->UCSRnA = UCSRA;
            this->UCSRnB = UCSRB;
            this->UCSRnC = UCSRC;
            this->UDRn = UDR;
            this->UBRRnH = UBRRH;
            this->UBRRnL = UBRRL;
        }

    public:
        inline boolean init(uint64_t USART_BAUDRATE) 
        {
            uint64_t regVal;

            *UCSRnB = 0x00;
            *UCSRnC = 0x00;

            *UCSRnB |= 0b00011000;   //(1 << RXEN0) | (1 << TXEN0);   Turn on the transmission and reception circuitry
            *UCSRnC |= 0b00000110;   //(1 << UCSZ00) | (1 << UCSZ01); Use 8-bit character sizes

            if(USART_BAUDRATE == 115200 && F_CPU == 16000000) {
                regVal = 8;

            } else if(USART_BAUDRATE == 9600 && F_CPU == 16000000) {
                regVal = 103;
            }
            else {
                regVal = (((F_CPU / (USART_BAUDRATE * PrescalerValue))) - 1);
            }

            
            *UBRRnH = (regVal >> 8); // Load upper 8-bits of the baud rate value into the high byte of the UBRR register
            *UBRRnL = regVal;        // Load lower 8-bits of the baud rate value into the low byte of the UBRR register
        }

        inline boolean dataAvailable() {
            //1 << RXC
            return ((*UCSRnA & 0x80) == 0x80); //MAX 2 byte 
        }

        inline uint8_t read() {
            return (*UDRn);
        }

        inline void write(uint8_t value) {
            //1 << UDRE
            while ((*UCSRnA & (0b00100000)) == 0) {}; // Do nothing until UDR is ready for more data to be written to it
            *UDRn = value;                   
        }

        inline boolean attachInterrupt(void (*userFunc)(void), uint8_t InterruptType) 
        {
            switch (InterruptType) {
                case INTERRUPT_ON_RX_COMPLETE: {
                    *UCSRnB |= (1 << RXCIE0);
                    intFunc[0 + 3*K] = userFunc;
                    break;
                }
                case INTERRUPT_ON_TX_COMPLETE: {
                    *UCSRnB |= (1 << TXCIE0);
                    intFunc[1 + 3*K] = userFunc;
                    break;
                }
                case INTERRUPT_ON_DATA_REGISTER_EMPTY: {
                    *UCSRnB |= (1 << UDRIE0);
                    intFunc[2 + 3*K] = userFunc;
                    break;
                }
                default: {
                    return false;
                }
            }
            return true;
        }
    
    inline boolean detachInterrupt(uint8_t InterruptType) 
    {
        switch (InterruptType) {
            case INTERRUPT_ON_RX_COMPLETE: {
                intFunc[0 + 3*K] = nothing;
                *UCSRnB &= ~0b10000000;   //(1 << RXCIEn);
                break;
            }
            case INTERRUPT_ON_TX_COMPLETE: {
                *UCSRnB &= ~0b01000000;   //(1 << TXCIEn);
                intFunc[1 + 3*K] = nothing;
                break;
            }
            case INTERRUPT_ON_DATA_REGISTER_EMPTY: {
                *UCSRnB &= ~0b00100000;   //(1 << UDRIEn);
                intFunc[2 + 3*K] = nothing;
                break;
            }
            default: {
                return false;
            }
        }
        return true;
    }
};


#if defined(__AVR_ATmega2560__)

class HardWareSerial1 : Interface_HardwareSerial<volatile uint8_t*, 1>
{
    public:
        HardWareSerial1() : Interface_HardwareSerial(&UCSR1A, &UCSR1B, &UCSR1C, &UDR1, &UBRR1H, &UBRR1L){};
        
        boolean init(uint64_t USART_BAUDRATE) {
            Interface_HardwareSerial::init(USART_BAUDRATE);
        }

        boolean attachInterrupt(void (*userFunc)(void), uint8_t InterruptType) {
            Interface_HardwareSerial::attachInterrupt(userFunc, InterruptType);
        }
        
        uint8_t read() {
          return Interface_HardwareSerial::read();
        }

        void write(uint8_t data) {
          Interface_HardwareSerial::write(data);
        }

        uint8_t available() {
          return Interface_HardwareSerial::dataAvailable();
        }

};

class HardWareSerial2 : Interface_HardwareSerial<volatile uint8_t*, 2>
{
    public:
        HardWareSerial2() : Interface_HardwareSerial(&UCSR2A, &UCSR2B, &UCSR2C, &UDR2, &UBRR2H, &UBRR2L) 
        {};
};

class HardWareSerial3 : Interface_HardwareSerial<volatile uint8_t*, 3>
{
    public:
        HardWareSerial3() : Interface_HardwareSerial(&UCSR3A, &UCSR3B, &UCSR3C, &UDR3, &UBRR3H, &UBRR3L) 
        {};
};



#endif







#endif //HARDWARE_SWERIAL_H