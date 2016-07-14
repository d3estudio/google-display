#include <avr/io.h>
#include <avr/interrupt.h>

// zero cross detect*
#define DETECT 2

// trigger pulse width (counts)
#define PULSE 4

// Defines the FSM state to ~wating for a command~
#define WAITING 0

// Defines the FSM state to ~waiting for payload~,
// which given what we are actually doing here, only
// means that the next byte should be a byte defining
// all lights state.
#define WAITING_PAYLOAD 1

// Identify command, called from our raspberry to
// make sure it is actually communicating with
// the raspberry (who knows, right?)
#define COMMAND_IDENTIFY 0x20

// ~get~ command. Returns the lightsState through
// serial to the raspberry. Useful if eventually
// we need a syncing mechanism.
#define COMMAND_GET 0x21

// ~set~ command. Sets the light state.
#define COMMAND_SET 0x22

// Reset command. Actually only resets the lightsState to zero.
// Useful if we need to perform any other operation upon reset
// without actually resetting the board. .-.
#define COMMAND_RESET 0x23

int lightsState = 0;
int state = WAITING;

void updatePinState(int gate, int offset, bool negate) {
  digitalWrite(gate, (lightsState & offset) == offset && !negate ? HIGH : LOW);
}

// Called by other methods whenever the lights state should be updated.
void updateLightsState(bool negate) {
  // TODO: Read lightsState, and update accordingly.
  // maybe using updatePinState to perform the bitwise
  // comparation and do the triac magic right after?
  updatePinState(3, 0x1, negate);
  updatePinState(4, 0x2, negate);
  updatePinState(5, 0x4, negate);
  updatePinState(6, 0x8, negate);
  updatePinState(7, 0x10, negate);
  updatePinState(8, 0x20, negate);
  updatePinState(9, 0x40, negate);
  updatePinState(10, 0x80, negate);
  attachInterrupt(0, zeroCrossingInterrupt, RISING);
}


//////////////////////////////////////////////////////////////////////////
// Other things.

void processCommand(int incomingByte) {
  switch (incomingByte) {
    case COMMAND_IDENTIFY:
      Serial.print("A");
      state = WAITING;
      break;
    case COMMAND_GET:
      Serial.write(lightsState);
      state = WAITING;
      break;
    case COMMAND_RESET:
      lightsState = 0;
      updateLightsState(false);
      state = WAITING;
      break;
    case COMMAND_SET:
      state = WAITING_PAYLOAD;
      break;
  }
}

void setup() {
  Serial.begin(9600);
  for(int i = 3; i < 11; i++) {
    pinMode(i, OUTPUT);
  }
  // set up pins
  pinMode(DETECT, INPUT);     //zero cross detect
  digitalWrite(DETECT, HIGH); //enable pull-up resistor

  // set up Timer1
  //(see ATMEGA 328 data sheet pg 134 for more details)
  OCR1A = 100;      //initialize the comparator
  TIMSK1 = 0x03;    //enable comparator A and overflow interrupts
  TCCR1A = 0x00;    //timer control registers set for
  TCCR1B = 0x00;    //normal operation, timer disabled
}


//Interrupt Service Routines

void zeroCrossingInterrupt(){ //zero cross detect
  TCCR1B=0x04; //start timer with divide by 256 input
  TCNT1 = 0;   //reset timer - count from zero
}

ISR(TIMER1_COMPA_vect){ //comparator match
  updateLightsState(false);
  TCNT1 = 65536-PULSE;      //trigger pulse width
}

ISR(TIMER1_OVF_vect){ //timer1 overflow
  updateLightsState(true);
  TCCR1B = 0x00;          //disable timer stopd unintended triggers
}

void loop() {
  if(Serial.available() > 0) {
    int incomingByte = Serial.read();
    switch (state) {
      case WAITING:
        processCommand(incomingByte);
        break;
      case WAITING_PAYLOAD:
        lightsState = incomingByte;
        updateLightsState(false);
        state = WAITING;
        break;
      default:
        break;
    }
  }
}
