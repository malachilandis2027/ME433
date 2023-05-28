#include "nu32dip.h" // constants, functions for startup and UART
#include "i2c_master_noint.h" // i2c

// Pin connections to MPU6050 IMU
// SCL1 - pin 17
// SDA1 - pin 18

int main(void) {
    // First get the WHO_AM_I number from the IMU
    // If this doesn't work, get stuck in infinite loop with green LED on
    
}

