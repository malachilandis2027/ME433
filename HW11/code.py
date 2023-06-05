from ulab import numpy as np
import time

entries = 1024
output = np.zeros(entries)

frequencies = [2,5,10] # Given in Hz
final_time = 10
times = np.linspace(0,30,entries)

for freq in frequencies:
    output = output + np.sin(2*np.pi*freq*times)

Fs = entries/final_time # sample rate
Ts = 1.0/Fs; # sampling interval
ts = np.arange(0,final_time,Ts) # time vector
k = np.arange(entries)
T = entries/Fs
Y = np.fft.fft(output)[0]/entries # fft computing and normalization

while(1):
    for i in range(int(entries/2)):
        print(""+str(Y[i])+",")
        time.sleep(0.005)
    time.sleep(10)