#include "nu32dip.h" // constants, functions for startup and UART
#include "uart2.h"

#define leftThreshold -0.1 // if the parameter from the camera is less than this, turn left
#define rightThreshold 0.1 // if the parameter from the camera is greater than this, turn right
#define leftMotorTurning 0.5 // when turning left, decrease left motor speed to this portion of max
#define rightMotorTurning 0.5 // when turning right, decrease right motor speed to this portion of max

void setSteering(float);

int main(void) {
  NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
  UART2_Startup(); // get the UART2 working
  
  RPB15Rbits.RPB15R = 0b0101; // Set B15 to OC1
  RPB11Rbits.RPB11R = 0b0101; // Set B11 to OC2
  
  T2CONbits.TCKPS = 0b101; // Timer2 prescaler N=32 (1:32)
  PR2 = 51200-1;           // Timer2 period = (PR2+1) * N * (1/48000000) = 30 kHz
  TMR2 = 0;                // initial TMR2 count is 0
  OC1CONbits.OCM = 0b110;  // PWM mode without fault pin; other OC1CON bits are defaults
  OC2CONbits.OCM = 0b110;  // PWM mode without fault pin; other OC2CON bits are defaults
  OC1CONbits.OCTSEL = 0;   // Use timer2
  OC2CONbits.OCTSEL = 0;   // Use timer2
  OC1RS = 1;               // OC1 duty cycle = OC1RS/(PR2+1)
  OC2RS = 1;               // OC2
  OC1R = 1;                // initialize before turning OC1 on; afterward it is read-only
  OC2R = 1;                // OC2
  T2CONbits.ON = 1;        // turn on Timer2
  OC1CONbits.ON = 1;       // turn on OC1
  OC2CONbits.ON = 1;       // turn on OC2
  
  TRISBbits.TRISB12 = 0; // Make B12 an output pin
  TRISBbits.TRISB14 = 0; // Make B14 an output pin
  LATBbits.LATB12 = 0; // Turn on B12
  LATBbits.LATB14 = 0; // Turn on B14
  
  char message2[100]; // to hold messages from the Pico
  
  while (1) {
      // wait for input over UART2 from the Pico
      int com = 0;
      // uart2_flag() is 1 when uart2 has rx a message and sprintf'd it into a value
      if(get_uart2_flag()){
        set_uart2_flag(0); // set the flag to 0 to be ready for the next message
        com = get_uart2_value();
        sprintf(message2,"%f\r\n",com);
        NU32DIP_WriteUART1(message2);
      }
      setSteering(com);
  }
}

void setSteering(float error) {
    // Sets the servo to a position between 0 and 1 by varying the duty cycle of OC1
    float leftDuty = 1; // initialize duty cycle variable
    float rightDuty = 1; // initialize duty cycle variable
    
    if (error > rightThreshold) { // line is too far to the right
        rightDuty = rightMotorTurning;
        NU32DIP_YELLOW = 0;
    }
    else if (error < leftThreshold) { // line is too far to the left
        leftDuty = leftMotorTurning;
        NU32DIP_YELLOW = 0;
    }
    else { // line is (hopefully) in the middle
        NU32DIP_YELLOW = 1;
    }
    OC1RS = leftDuty*PR2;
    OC2RS = rightDuty*PR2;
}
		
