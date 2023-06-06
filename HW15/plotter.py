# get a line of raw bitmap and plot the components
import serial
import numpy as np
ser = serial.Serial('/dev/ttyACM0',230400) # the name of your Pico port
print('Opening port: ')
print(ser.name)

ser.write(b'hi\r\n') # send a newline to request data
data_read = ser.read_until(b'\n',50) # read the echo

sampnum = 0
index = 0
raw = []
reds = []
greens = []
blues = []
bright = []

# Pico sends back index and raw pixel value
while sampnum < 60: # width of bitmap
    data_read = ser.read_until(b'\n',50) # read until newline
    data_text = str(data_read,'utf-8') # convert bytes to string
    data = list(map(int,data_text.split())) # convert string to values

    if(len(data)==2):
        index = data[0]
        raw.append(data[1])
        reds.append(((data[1]>>5)&0x3F)/0x3F*100) # red value is middle 6 bits
        greens.append((data[1]&0x1F)/0x1F*100) # green value is rightmost 5 bits
        blues.append(((data[1]>>11)&0x1F)/0x1F*100) # blue vale is leftmost 5 bits
        bright.append((data[1]&0x1F)+((data[1]>>5)&0x3F)+((data[1]>>11)&0x1F)) # sum of colors
        sampnum = sampnum + 1

smoothingKernel = [0.006, 0.061, 0.242, 0.383, 0.242, 0.061, 0.006]
edgeKernel = [-0.5,0,0.5]
brightSmoothed = np.convolve(bright, smoothingKernel, 'same')
brightEdge = np.convolve(bright, edgeKernel, 'same')
redEdge = np.abs(np.convolve(reds, edgeKernel, 'same'))
greenEdge = np.abs(np.convolve(greens, edgeKernel, 'same'))
blueEdge = np.abs(np.convolve(blues, edgeKernel, 'same'))
newMetric = (redEdge+greenEdge+blueEdge)/100
smoothMetric = np.convolve(newMetric,smoothingKernel,'same')

print(np.linspace(1,60,60)*np.linspace(1,60,60))
COM = np.sum(np.linspace(1,60,60)*newMetric)/(30*np.sum(newMetric)) - 1
print(COM)

# print the raw color as a 16bit binary to double check bitshifting
# for i in range(len(reds)):
#     print(f"{raw[i]:#018b}")

# plot the colors 
import matplotlib.pyplot as plt 
x = range(len(reds)) # time array
# plt.plot(x,reds,'r*-',x,greens,'g*-',x,blues,'b*-')
plt.plot(x,newMetric,'k*-')
plt.plot(x,smoothMetric,'r*-')
# plt.plot(x,blueEdge,'b*-')
# plt.plot(x,redEdge,'r*-')
# plt.plot(x,greenEdge,'g*-')
plt.ylabel('color')
plt.xlabel('position')
plt.show()

# be sure to close the port
ser.close()