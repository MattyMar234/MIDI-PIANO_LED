#ifndef CODA_H
#define CODA_H


template<uint16_t SIZE>
class Coda
{
    private:
        uint8_t array[SIZE];
        uint16_t index = 0;

    public:
        Coda() {
            this->index = 0;
        }

        uint16_t size() {
            return this->index;
        }

        void push(uint8_t data) {
            if(index < SIZE) {
                array[index++] = data;
            }else {
                array[index] = data;
            }
        }

        uint8_t pop() {
            if(index == 0) {
                return 0;
            }

            uint8_t data = array[0];
            for(register uint16_t i = 0; i < index - 1; i++) {
                array[i] = array[i + 1];
            }
            index--;

            return data;
        }
};

#endif