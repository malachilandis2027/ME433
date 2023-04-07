#include "nu32dip.h" // constants, functions for startup and UART

int main(void) {
  char message[100];
  
  NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
  while (1) {
	if (!NU32DIP_USER){ // User button pressed
        float current_number = 0;
        for (int i = 0; i < 100; i++) {
            _CP0_SET_COUNT(0);
            current_number = sin(2*3.1415*(((float) i)/100));
            sprintf(message, "%f", current_number);
            NU32DIP_WriteUART1(message);
            NU32DIP_WriteUART1("\r\n");
            while (_CP0_GET_COUNT()<240000) {}
        }
	}
  }
}

		
