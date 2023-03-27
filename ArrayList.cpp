#include "ArrayList.h"

template<typename Type, uint8_t N>
ArrayList<Type,N>::ArrayList(){
    this->size = 0;
}


template<typename Type, uint8_t N>
bool ArrayList<Type,N>::add(Type element) 
{
    //ArrayNode<T> *NewNode = (ArrayNode<T>*)malloc(sizeof(ArrayNode<T>));
    register ArrayNode<Type> *NewNode = new ArrayNode<Type>();
    NewNode->data = element;

    if(this->size == 0) {
        fistNode = NewNode;
        lastNode = NewNode;
        this->size++;
    }
    else if(this->size < N){
        lastNode->nextNode = NewNode;
        NewNode->previusNode = lastNode;
        lastNode = NewNode;

        this->size++;
    }
    else {
        return false;
    }

    return true;
}


template<typename Type, uint8_t N>
Type ArrayList<Type,N>::get(register int index) 
{
    if(index < 0 || index > this->size || index > N) {
        return NULL;
    }

    register ArrayNode<Type> *pNode = fistNode;
    
    for(register uint8_t i = 0; i < index; i++)
        pNode = pNode->nextNode;

    return pNode->data;
} 


template<typename Type, uint8_t N>
bool ArrayList<Type,N>::remove(register int index) {

    if(this->size == 0 || index < 0 || index > this->size - 1 || index > N) {
        return false;
    }

    register ArrayNode<Type> *pNode = fistNode;
    
    //arrivo fino al punto
    for(uint8_t i = 0; i < index; i++)
        pNode = pNode->nextNode;
    
    
    //se è l'ultimo elemento
    if(this->size == 1) {
        free(pNode);
        fistNode = NULL;
        lastNode = NULL;
        this->size--;
    }
    else 
    {
        if(pNode == fistNode) {
            pNode->nextNode->previusNode = NULL;
            fistNode = pNode->nextNode;
        }
        else if(pNode == lastNode) {
            lastNode = pNode->previusNode;
            lastNode->nextNode = NULL;
        }
        else {
            register ArrayNode<Type> *pNext    = pNode->nextNode;
            register ArrayNode<Type> *pPrevius = pNode->previusNode;

            pPrevius->nextNode = pNext;
            pNext->previusNode = pPrevius;  
        }

        free(pNode);
        this->size--;
    }
}

template<typename Type, uint8_t N>
bool ArrayList<Type,N>::push(Type data) {
    return add(data);
}

template<typename Type, uint8_t N>
Type ArrayList<Type,N>::pop() 
{
    register uint8_t size_ = this->size - 1;
    
    Type p = get(size_);
    remove(size_);

    return p;
}

template<typename Type, uint8_t N>
Type ArrayList<Type,N>::front() 
{
    Type p = get(0);
    remove(0);
    return p;
}
    

template<typename Type, uint8_t N>
void ArrayList<Type,N>::print()
{
    Serial.print(F("Data: ["));
    
    for(uint8_t i = 0; i < lenght(); i++) {
        Serial.print((int)this->get(i));
        Serial.print((i < lenght() -1) ? ", " : "");
    }
    Serial.print(F("]"));
}



/*template<typename T>
int ArrayList<T>::size() {
    return this->size;
}*/
