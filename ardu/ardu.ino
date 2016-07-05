#include <avr/io.h>
#include <avr/interrupt.h>

#define DETECT 2  //zero cross detect
#define PULSE 4   //trigger pulse width (counts)
int i=483;
int GATE;
int incomingByte;
int counter = 0;

void setup(){

  Serial.begin(921600);

  // set up pins
  pinMode(DETECT, INPUT);     //zero cross detect
  digitalWrite(DETECT, HIGH); //enable pull-up resistor
  pinMode(4, OUTPUT);      //triac gate control
  pinMode(5, OUTPUT);      //triac gate control
  pinMode(6, OUTPUT);      //triac gate control
  pinMode(7, OUTPUT);      //triac gate control
  pinMode(9, OUTPUT);      //triac gate control
  pinMode(10, OUTPUT);      //triac gate control
  pinMode(11, OUTPUT);      //triac gate control
  pinMode(12, OUTPUT);      //triac gate control

  // set up Timer1
  //(see ATMEGA 328 data sheet pg 134 for more details)
  OCR1A = 100;      //initialize the comparator
  TIMSK1 = 0x03;    //enable comparator A and overflow interrupts
  TCCR1A = 0x00;    //timer control registers set for
  TCCR1B = 0x00;    //normal operation, timer disabled


  // set up zero crossing interrupt
    //IRQ0 is pin 2. Call zeroCrossingInterrupt
    //on rising signal

}

//Interrupt Service Routines

void zeroCrossingInterrupt(){ //zero cross detect
  TCCR1B=0x04; //start timer with divide by 256 input
  TCNT1 = 0;   //reset timer - count from zero
}

ISR(TIMER1_COMPA_vect){ //comparator match
  digitalWrite(GATE,HIGH);  //set triac gate to high
  TCNT1 = 65536-PULSE;      //trigger pulse width
}

ISR(TIMER1_OVF_vect){ //timer1 overflow
  digitalWrite(GATE,LOW); //turn off triac gate
  TCCR1B = 0x00;          //disable timer stopd unintended triggers
}

void animation (int index) {
  GATE = index;
  delay(100);
  attachInterrupt(0, zeroCrossingInterrupt, RISING);
  i=483;
  for(int j = 483; j > 100; j--){
    OCR1A = j;
    delay(5);
  }
  for(int i = 100; i < 483; i++){
    OCR1A = i;
    delay(5);
  }
}

void loop(){
  if (Serial.available() > 0) {
    incomingByte = Serial.read();
    counter = incomingByte;
    if(incomingByte == '1'){
      digitalWrite(5,LOW);  //set triac gate to high
      digitalWrite(6,LOW);  //set triac gate to high
      digitalWrite(7,LOW);  //set triac gate to high
      digitalWrite(9,LOW);  //set triac gate to high
      digitalWrite(10,LOW);  //set triac gate to high
      digitalWrite(11,LOW);  //set triac gate to high
      digitalWrite(12,LOW);  //set triac gate to high
      animation(4);
    }
    if(incomingByte == '2'){
      digitalWrite(4,LOW);  //set triac gate to high
      digitalWrite(6,LOW);  //set triac gate to high
      digitalWrite(7,LOW);  //set triac gate to high
      digitalWrite(9,LOW);  //set triac gate to high
      digitalWrite(10,LOW);  //set triac gate to high
      digitalWrite(11,LOW);  //set triac gate to high
      digitalWrite(12,LOW);  //set triac gate to high
      animation(5);
    }
    if(incomingByte == '3'){
      digitalWrite(4,LOW);  //set triac gate to high
      digitalWrite(5,LOW);  //set triac gate to high
      digitalWrite(7,LOW);  //set triac gate to high
      digitalWrite(9,LOW);  //set triac gate to high
      digitalWrite(10,LOW);  //set triac gate to high
      digitalWrite(11,LOW);  //set triac gate to high
      digitalWrite(12,LOW);  //set triac gate to high
        animation(6);
    }
    if(incomingByte == '4'){
      digitalWrite(4,LOW);  //set triac gate to high
      digitalWrite(5,LOW);  //set triac gate to high
      digitalWrite(6,LOW);  //set triac gate to high
      digitalWrite(9,LOW);  //set triac gate to high
      digitalWrite(10,LOW);  //set triac gate to high
      digitalWrite(11,LOW);  //set triac gate to high
      digitalWrite(12,LOW);  //set triac gate to high
        animation(7);
    }
    if(incomingByte == '8'){
      digitalWrite(4,LOW);  //set triac gate to high
      digitalWrite(5,LOW);  //set triac gate to high
      digitalWrite(6,LOW);  //set triac gate to high
      digitalWrite(7,LOW);  //set triac gate to high
      digitalWrite(10,LOW);  //set triac gate to high
      digitalWrite(11,LOW);  //set triac gate to high
      digitalWrite(12,LOW);  //set triac gate to high
        animation(9);
    }
    if(incomingByte == '7'){
      digitalWrite(4,LOW);  //set triac gate to high
      digitalWrite(5,LOW);  //set triac gate to high
      digitalWrite(6,LOW);  //set triac gate to high
      digitalWrite(7,LOW);  //set triac gate to high
      digitalWrite(9,LOW);  //set triac gate to high
      digitalWrite(11,LOW);  //set triac gate to high
      digitalWrite(12,LOW);  //set triac gate to high
        animation(10);
    }
    if(incomingByte == '6'){
      digitalWrite(4,LOW);  //set triac gate to high
      digitalWrite(5,LOW);  //set triac gate to high
      digitalWrite(6,LOW);  //set triac gate to high
      digitalWrite(7,LOW);  //set triac gate to high
      digitalWrite(9,LOW);  //set triac gate to high
      digitalWrite(10,LOW);  //set triac gate to high
      digitalWrite(12,LOW);  //set triac gate to high
        animation(11);
    }
    if(incomingByte == '5'){
      digitalWrite(4,LOW);  //set triac gate to high
      digitalWrite(5,LOW);  //set triac gate to high
      digitalWrite(6,LOW);  //set triac gate to high
      digitalWrite(7,LOW);  //set triac gate to high
      digitalWrite(9,LOW);  //set triac gate to high
      digitalWrite(10,LOW);  //set triac gate to high
      digitalWrite(11,LOW);  //set triac gate to high
        animation(12);
    }
  }
  if(counter == 0 || incomingByte == 'A'){
    Serial.println("arduino");
  }
}
