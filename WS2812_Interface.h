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
            pixels = Adafruit_NeoPixel(PixelsCount, Pixels_PIN, NEO_GRB + NEO_KHZ800);
            PixelsCount = PixelsCount;
            Pixels_PIN = Pixels_PIN;

            pixels.begin();
            pixels.clear();
            //pixels.show();
            //pixels.setBrightness(brightness);
        }

        inline void setBrightness(uint8_t brightness) {
            pixels.setBrightness(brightness);
        }

        inline void refresh() {
            //Serial.println("pixels show!");
            pixels.show();
        }

        inline void clear() {
            pixels.clear();
        }

        inline void SetLedColor(uint8_t register number, uint8_t register r, uint8_t register g, uint8_t register b) {
            Serial.print("pixels: n = ");   Serial.print(number);
            Serial.print(" r = ");          Serial.print(r);
            Serial.print(" g = ");          Serial.print(g);
            Serial.print(" b = ");          Serial.println(b);
            pixels.setPixelColor(number, pixels.Color(r,g,b));
        }


};


#endif //WS2812_INTERFACE
