
#ifndef ARRAYLIST_H
#define ARRAYLIST_H

//#include <iostream>
#include <Arduino.h>

#define MAX_LENGHT 128



template<typename Type>
class ArrayNode
{
    private:
    public:
        ArrayNode<Type> *nextNode;
        ArrayNode<Type> *previusNode;
        Type data;
};

template<typename Type>
class ArrayList
{
    private:
        int size;
        ArrayNode<Type> *fistNode;
        ArrayNode<Type> *lastNode;
    
    public:
        ArrayList(); 

        bool add(Type element);
        bool remove(int index);
        Type get(int index);
        void print();

        int lenght() const {
            return this->size;
        }

};


#endif //ARRAYLISTH