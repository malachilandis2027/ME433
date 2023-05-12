# Adapted from https://www.arc.id.au/FilterDesign.html
# Inputs:
#   Fs [Hz] - sampling frequency
#   Fa [Hz] - lower bound on band pass
#   Fb [Hz] - upper bound on band pass
#   N - number of points in filter
#   Att [dB] - desired attenuation

import numpy as np

def kaiserBesselFIR(Fs, Fa, Fb, N, Att):
    Np = int((N-1)/2)
    def Ino(x):
        d = 2
        ds = x**2/(d**2)
        s = 1 + ds
        while (ds > s*1e-6):
            d = d+2
            ds = ds*x**2/(d**2)
            s = s + ds
        return s
    
    
    A = np.zeros(N)
    A[0] = 2*(Fb-Fa)/Fs;
    for j in range(1,Np+1):
        A[j] = (np.sin(2*j*np.pi*Fb/Fs)-np.sin(2*j*np.pi*Fa/Fs))/(j*np.pi)
        
        
    if (Att<21):
        Alpha = 0
    elif (Att>50):
        Alpha = 0.1102*(Att-8.7)
    else:
        Alpha = 0.5842*(Att-21)**0.4 + 0.07886*(Att-21)
        
        
    # Window the ideal response with the Kaiser-Bessel window
    Inoalpha = Ino(Alpha)
    H = np.zeros(N)
    for j in range(0,Np+1):
        H[Np+j] = A[j]*Ino(Alpha*(1-((j-Np)**2/(Np**2)))**0.5)/Inoalpha
    for j in range(0,Np):
        H[j] = H[N-1-j]
    return H

w = kaiserBesselFIR(10000,0,200,499,21)