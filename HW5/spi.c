
#include <proc/p32mx170f256b.h>

// initialize SPI1
#define CS LATBbits.LATB15
void initSPI() {
    // Pin B14 has to be SCK1
    // Turn off analog pins
    // Make an output pin for CS
    TRISBbits.TRISB15 = 0; // Setting B15 to output (0) pin 25
    CS = 1; // Setting chip select high (not talking to DAC at the moment)
    // Set SDO1
    RPB13Rbits.RPB13R = 0b0011; // Set the SFR register to SDO1 (pin 24)
    // Set SDI1
    SDI1Rbits.SDI1R = 0b0011; // Set the SFR register to RPD11 (pin 22)
    // Set SS1

    // setup SPI1
    SPI1CON = 0; // turn off the spi module and reset it
    SPI1BUF; // clear the rx buffer by reading from it
    SPI1BRG = 1000; // 1000 for 24kHz, 1 for 12MHz; // baud rate to 10 MHz [SPI1BRG = (48000000/(2*desired))-1]
    SPI1STATbits.SPIROV = 0; // clear the overflow bit
    SPI1CONbits.CKE = 1; // data changes when clock goes from hi to lo (since CKP is 0)
    SPI1CONbits.MSTEN = 1; // master operation
    SPI1CONbits.MODE32 = 0; // part 1 of enabling 16-bit communication
    SPI1CONbits.MODE16 = 1; // part 2 of enabling 16-bit communication
    SPI1CONbits.ON = 1; // turn on spi 
}


// send 16 bits via spi and return the response
unsigned short spi_io(unsigned short o) {
    CS = 0; // Set low to start talking to chip
    SPI1BUF = o;
    while(!SPI1STATbits.SPIRBF) { // wait to receive the byte
      ;
    }
    CS = 1; // Set high to stop talking to chip
    return SPI1BUF;
}