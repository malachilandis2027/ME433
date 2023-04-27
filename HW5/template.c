#include "nu32dip.h" // constants, functions for startup and UART
#include "spi.h" // SPI communication

short sineOut(float freq, int cycles, int time) {
    // Takes in a target frequency, current time in cycles, and number of cycles per loop
    // Outputs a short that can be sent directly to the DAC
    // Calculate the value of sine at this time
    short sineVal = 511.5*sin(2*3.1415*freq*((float)time/(float)cycles))+512;
    // Modify the value for the DAC
    sineVal = sineVal<<2; // Left shift by two to add the zeros on the right side
    sineVal = sineVal|0b0111000000000000; // Add the 4 leading bits, channel A
    return sineVal;
}

short triOut(int cycles, int time) {
    // Takes in a target frequency, current time in cycles, and number of cycles per loop
    // Outputs a short that can be sent directly to the DAC
    // Calculate the value of a triangular ramp at this time
    short triVal = 1023.0*(float)time/(float)cycles;
    // Modify the value for the DAC
    triVal = triVal<<2; // Left shift by two to add the zeros on the right side
    triVal = triVal|0b1111000000000000; // Add the 4 leading bits, channel B
    return triVal;
}

int main(void) {
  NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
  initSPI();
  char message[100];
  short sine;
  short tri;
  int time = 0;
  while (1) {
	if (!NU32DIP_USER){ // User button pressed
        _CP0_SET_COUNT(0);
        sine = sineOut(2.0, 200, time);
        spi_io(sine);
        tri = triOut(200, time);
        spi_io(tri);
//        sprintf(message, "%i", dummy);
//        NU32DIP_WriteUART1(message);
//        NU32DIP_WriteUART1("\r\n");
        time++; // increment the current time
        if (time == 200) {
            time = 0; // reset after 100 increments
        }
        while (_CP0_GET_COUNT()<120000) {} // 48000000 = 1s
	}
  }
}

		
