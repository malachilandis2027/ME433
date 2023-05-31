#include "nu32dip.h" // constants, functions for startup and UART
#include "i2c_master_noint.h" // i2c

// Pin connections to MCP23008 IO expander chip
// SCL1 - pin 17
// SDA1 - pin 18

#define MCP23008 0b0100000 // Address of IO expander
#define IODIR 0x00 // Input/output register
#define GPIO 0x09 // Pin read register
#define OLAT 0x0A // Pin write register

void setReg(unsigned char adr, unsigned char reg, unsigned char val) {
    // Sets the register on the addressed device to the value
    unsigned char writeAdr = adr<<1;
    i2c_master_start(); // Send start bit
    i2c_master_send(writeAdr); // Send the address of the device with the write bit set
    i2c_master_send(reg); // Send the register to be updated
    i2c_master_send(val); // Set the register to the value
    i2c_master_stop(); // Send stop bit
}

unsigned char readReg(unsigned char adr, unsigned char reg) {
    // Reads from the register on the addressed device
    unsigned char writeAdr = adr<<1;
    unsigned char readAdr = writeAdr&0b00000001;
    i2c_master_start(); // Send start bit
    i2c_master_send(writeAdr); // Send the address of the device with the write bit set
    i2c_master_send(reg); // Send the register to be updated
    i2c_master_restart(); // Send restart bit
    i2c_master_send(readAdr); // Send the address of the device with the read bit set
    unsigned char info = i2c_master_recv();
    i2c_master_ack(1);
    i2c_master_stop();
    return info;
}

int main(void) {
  NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
  setReg(MCP23008, IODIR, 0b01111111); // First set GP7 to output, GP0 to input
  
  unsigned char readResult; // Declare variable used to store the result of reading the inputs
  
  _CP0_SET_COUNT(0); // Set the core counter to zero, will be used to heartbeat
  while (1) { // Endless while to constantly check the button (GP0) and update the LED (GP7) to match
      readResult = readReg(MCP23008, GPIO);
      if (readResult&0b00000001 == 0b00000001) { // Check to see if GP0's bit is high
          setReg(MCP23008, OLAT, 0b10000000); // Set the GP7 high
      }
      else { // If the GP0 bit isn't high, then the LED (GP7) should be off
          setReg(MCP23008, OLAT, 0b00000000); // Set the GP7 low
      }
      if (_CP0_GET_COUNT() > 12000000) { // Heartbeat
          if (NU32DIP_GREEN == 1) {
              NU32DIP_GREEN = 0;
          }
          else {
              NU32DIP_GREEN = 1;
          }
      }
  }
}

		
