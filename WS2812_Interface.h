#ifndef WS2812_INTERFACE
#define WS2812_INTERFACE

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

class WS2812_interface
{
    private:
        Adafruit_NeoPixel pixels;
        uint8_t PixelsCount;
        uint8_t Pixels_PIN;

    public:
        WS2812_interface();
        
        inline void init(uint8_t PixelsCount, uint8_t Pixels_PIN, uint8_t brightness) {
            noInterrupts();
            pixels = Adafruit_NeoPixel(PixelsCount, Pixels_PIN, NEO_GRB + NEO_KHZ800);
            PixelsCount = PixelsCount;
            Pixels_PIN = Pixels_PIN;

            pixels.begin();
            pixels.clear();
            //pixels.show();
            //pixels.setBrightness(brightness);
            interrupts();
        }

        inline void setBrightness(uint8_t brightness) {
            noInterrupts();
            pixels.setBrightness(brightness);
            interrupts();

        }

        inline void refresh() {
            //Serial.println("pixels show!");
            noInterrupts();
            pixels.show();
            interrupts();
        }

        inline void clear() {
            noInterrupts();
            pixels.clear();
            pixels.show();
            interrupts();
        }

        inline void SetLedColor(uint8_t register number, uint8_t register r, uint8_t register g, uint8_t register b) {
            //Serial.print("pixels: n = ");   Serial.print(number);
            //Serial.print(" r = ");          Serial.print(r);
            //Serial.print(" g = ");          Serial.print(g);
            //Serial.print(" b = ");          Serial.println(b);
            
            noInterrupts();
            pixels.setPixelColor(number, pixels.Color(r,g,b));
            interrupts();
        }

        inline void SetLedColor_by_HUE(uint8_t register number, uint16_t register hue) {
            noInterrupts();
            pixels.setPixelColor(number, pixels.ColorHSV(hue, 0xFF, 0xFF));
            interrupts();
        }
        inline void SetLedColor_by_HUE(uint8_t register number, uint16_t register hue, uint8_t brightness) {
            noInterrupts();
            pixels.setPixelColor(number, pixels.ColorHSV(hue, 0xFF, brightness));
            interrupts();
        }
        inline void SetLedColor_by_HUE(uint8_t register number, uint16_t register hue, uint8_t brightness, uint8_t saturation) {
            noInterrupts();
            pixels.setPixelColor(number, pixels.ColorHSV(hue, saturation, brightness));
            interrupts();
        }


};


#endif //WS2812_INTERFACE
