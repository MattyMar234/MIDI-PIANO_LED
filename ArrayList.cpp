#include "ArrayList.h"

template<typename Type>
ArrayList<Type>::ArrayList(){
    this->size = 0;
}


template<typename Type>
bool ArrayList<Type>::add(Type element) 
{
    //ArrayNode<T> *NewNode = (ArrayNode<T>*)malloc(sizeof(ArrayNode<T>));
    register ArrayNode<Type> *NewNode = new ArrayNode<Type>();
    NewNode->data = element;

    if(this->size == 0) {
        fistNode = NewNode;
        lastNode = NewNode;
        this->size++;
    }
    else if(this->size < MAX_LENGHT){
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


template<typename Type>
Type ArrayList<Type>::get(register int index) 
{
    if(index < 0 || index > this->size || index > MAX_LENGHT) {
        return NULL;
    }

    register ArrayNode<Type> *pNode = fistNode;
    
    for(register uint8_t i = 0; i < index; i++)
        pNode = pNode->nextNode;

    return pNode->data;
} 


template<typename Type>
bool ArrayList<Type>::remove(register int index) {

    if(this->size == 0 || index < 0 || index > this->size - 1 || index > MAX_LENGHT) {
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

template<typename Type>
void ArrayList<Type>::print()
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
