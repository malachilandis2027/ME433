#include "nu32dip.h" // constants, functions for startup and UART

void blink(int, int); // blink the LEDs function

int main(void) {
  // char message[100];
  char blinks[100];
  char period[100];
  int b;
  int p;
  
  NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
  while (1) {
    // NU32DIP_ReadUART1(message, 100); // wait here until get message from computer
    // NU32DIP_WriteUART1(message); // send message back
    // NU32DIP_WriteUART1("\r\n"); // carriage return and newline
    NU32DIP_ReadUART1(blinks, 100); // wait to receive the number of blinks
    NU32DIP_WriteUART1(blinks); // send the number of blinks back
    NU32DIP_WriteUART1("\r\n"); // carriage return and newline
    NU32DIP_ReadUART1(period, 100); // wait to receive the blink period
    NU32DIP_WriteUART1(period); // send the period back
    NU32DIP_WriteUART1("\r\n"); // carriage return and newline
    sscanf(blinks, "%d", &b); // convert blinks char array into int
    sscanf(period, "%d", &p); // convert period char array into int
	if (NU32DIP_USER){
		// blink(5, 500); // 5 times, 500ms each time
        blink(b, p);
	}
  }
}

// blink the LEDs
void blink(int iterations, int time_ms){
	int i;
	unsigned int t;
	for (i=0; i< iterations; i++){
		NU32DIP_GREEN = 0; // on
		NU32DIP_YELLOW = 1; // off
		t = _CP0_GET_COUNT(); // should really check for overflow here
		// the core timer ticks at half the SYSCLK, so 24000000 times per second
		// so each millisecond is 24000 ticks
		// wait half in each delay
		while(_CP0_GET_COUNT() < t + 12000*time_ms){}
		
		NU32DIP_GREEN = 1; // off
		NU32DIP_YELLOW = 0; // on
		t = _CP0_GET_COUNT(); // should really check for overflow here
		while(_CP0_GET_COUNT() < t + 12000*time_ms){}
	}
}
		
