#include "nu32dip.h" // constants, functions for startup and UART
#include "ws2812b.h"

int main(void) {
  NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
  ws2812b_setup();
  int offset = 360/8; // offset in hue between adjacent LEDs
  wsColor myColors[8]; // declare array of colors, one for each LED
//  wsColor testColor[1];
//  testColor[0] = HSBtoRGB(180, 0.5, 0.5);
//  char message[100];
//  sprintf(message,"Test color: %i",who);
//  NU32DIP_WriteUART1(message);
//  
  int counter = 0; // initialize counter to 0
  while (1) {
    _CP0_SET_COUNT(0);
	for (int i = 0; i < 8; i++) {
        myColors[i] = HSBtoRGB((i*offset+counter)%360, 1.0, 0.2);
    }
    ws2812b_setColor(myColors);
    while (_CP0_GET_COUNT()<240000) {} // 48000000 = 1s
    counter++;
    if (counter > 1000000) {
        counter = 0;
    }
  }
}

		
