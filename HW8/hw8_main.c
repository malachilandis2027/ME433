#include "nu32dip.h" // constants, functions for startup and UART
#include "i2c_master_noint.h"
#include "mpu6050.h"
#include <stdio.h>

void blink(int, int); // blink the LEDs function
void drawChar(unsigned char, unsigned char, unsigned char); // draw character at x,y location
void drawString(unsigned char*, unsigned int, unsigned char, unsigned char); // draw string at x,y location

int main(void) {
    NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
    init_mpu6050();
    ssd1306_setup();
	
	// char array for the raw data
    char data[14]; // 16 bits per piece of data, 7 pieces of data (accel x,y,z, gyro x,y,z, and temp)
	// floats to store the data
    float accelZ;

	// read whoami
    uint8_t who = whoami();
	// print whoami
    char message[100];
    sprintf(message,"%i",who);
    NU32DIP_WriteUART1(message);
	// if whoami is not 0x68, stuck in loop with LEDs on
    if (who != 0x68) {
        NU32DIP_YELLOW = 1;
        NU32DIP_GREEN = 1;
        while(1);
    }
	// wait to print until you get a newline
    char m_in[100];
    NU32DIP_ReadUART1(m_in,100);

    unsigned long time = 1;
    while (1) {
        _CP0_SET_COUNT(0);
        blink(1, 5);

        // read IMU
        burst_read_mpu6050(data);
		// convert data
        accelZ = conv_zXL(data);
        
        sprintf(message,"Z Accel: %f",accelZ);
        drawString(message,16,10,10);
        sprintf(message,"FPS: %f",1/float(time));
        drawString(message,12,10,1);
        
        // sprintf(message,"FPS: %f",1/time);
        // NU32DIP_WriteUART1(message);
        time = _CP0_GET_COUNT();
    }
}

// blink the LEDs
void blink(int iterations, int time_ms) {
    int i;
    unsigned int t;
    for (i = 0; i < iterations; i++) {
        NU32DIP_GREEN = 0; // on
        NU32DIP_YELLOW = 1; // off
        t = _CP0_GET_COUNT(); // should really check for overflow here
        // the core timer ticks at half the SYSCLK, so 24000000 times per second
        // so each millisecond is 24000 ticks
        // wait half in each delay
        while (_CP0_GET_COUNT() < t + 12000 * time_ms) {
        }

        NU32DIP_GREEN = 1; // off
        NU32DIP_YELLOW = 0; // on
        t = _CP0_GET_COUNT(); // should really check for overflow here
        while (_CP0_GET_COUNT() < t + 12000 * time_ms) {
        }
    }
}

// draw character
void drawChar(unsigned char letter, unsigned char x, unsigned char y) {
    unsigned char columnHex; // Char used to store the hex value of a column
    unsigned char color; // Char used to store the pixel's color (0 or 1)
    for (int i = 0; i < 5; i++){ // Loop over each element of the list (columns)
        columnHex = ASCII[letter-0x20][i];
        for (int j = 7; j > -1; j--) { // Looping over the row
            color = 0b00000001 & columnHex; // Get the value of the LSB of columnHex
            ssd1306_drawPixel(x+i,y+j,color); // Draw the pixel
            columnHex = columnHex>>1; // Right shift by 1 to access the next pixel
        }
    }
}

void drawString(unsigned char* message, unsigned int length, unsigned char x, unsigned char y) {
    ssd1306_clear();
    for (int i = 0; i < length; i++) {
        drawChar(message[i],x+5*i,y);
    }
    ssd1306_update();
}