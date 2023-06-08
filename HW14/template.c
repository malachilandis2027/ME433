#include "nu32dip.h" // constants, functions for startup and UART

#define servoMax 7500     // max duty cycle of the servo = 12.5% = 2.5ms
#define servoMin 4500     // max duty cycle of the servo = 12.5% = 2.5ms

void setServo(float);

int main(void) {
  NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
  U2RXRbits.U2RXR = 0b0000; // Set A1 to UART2 RX
  RPA3Rbits.RPA3R = 0b0010; // Set A3 to UART2 TX
  
  RPB15Rbits.RPB15R = 0b0101; // Set B15 to OC1
  RPB11Rbits.RPB11R = 0b0101; // Set B11 to OC2
  
  T2CONbits.TCKPS = 0b100; // Timer2 prescaler N=16 (1:16)
  PR2 = 59999;             // period = (PR2+1) * N * (1/48000000) = 50 Hz = 20ms
  TMR2 = 0;                // initial TMR2 count is 0
  OC1CONbits.OCM = 0b110;  // PWM mode without fault pin; other OC1CON bits are defaults
  OC1CONbits.OCTSEL = 0;   // Use timer2
  OC1RS = 6000;            // duty cycle = OC1RS/(PR2+1) = 10% = 2ms
  OC1R = 6000;              // initialize before turning OC1 on; afterward it is read-only
  T2CONbits.ON = 1;        // turn on Timer2
  OC1CONbits.ON = 1;       // turn on OC1
  
  float counts = 0;        // counts used for the sine wave
  float position = 0.5;    // maps from 0 - 1 >>> 0 - 180 degrees
  
  setServo(position);
  
  while (1) {
      _CP0_SET_COUNT(0);
      
      position = 0.5*(sin(2*3.1415*0.25*counts/1000) + 1);
      setServo(position);
      
      while (_CP0_GET_COUNT() < 24000000 / 1000) {} // Delay for 0.001 s
      counts++;
  }
}

void setServo(float position) {
    // Sets the servo to a position between 0 and 1 by varying the duty cycle of OC1
    OC1RS = ((servoMax-servoMin)*position + servoMin);
}
		
